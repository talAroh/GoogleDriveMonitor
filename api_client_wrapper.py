from __future__ import print_function
import logging

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client import file, client, tools
from typing import List, Tuple
from settings import CREDS_FILE_PATH
from consts import (SCOPES, DRIVE_SERVICE_NAME, DRIVE_API_VERSION, DRIVE_ACTIVITY_SERVICE_NAME,
                    DRIVE_ACTIVITY_API_VERSION, PUBLIC_EXPOSURE_PERMISSION_ID, ACTIVITY_PAGE_SIZE)
from utils import get_unix_time_in_ms, is_file_publicly_exposed
import datetime

logger = logging.getLogger(__name__)


class APIClientWrapper:

    def __init__(self):
        try:
            self._create_creds()
            self.drive = discovery.build(DRIVE_SERVICE_NAME, DRIVE_API_VERSION, http=self.creds.authorize(Http()))
            self.drive_activity = discovery.build(DRIVE_ACTIVITY_SERVICE_NAME, DRIVE_ACTIVITY_API_VERSION,
                                                  http=self.creds.authorize(Http()))
            self.last_activity_check = get_unix_time_in_ms(datetime.datetime.now())
        except Exception as e:
            logger.exception(e)
            raise Exception('Failed to create APIClientWrapper: {e}')

    def _create_creds(self):
        store = file.Storage('storage.json')
        self.creds = store.get()
        if not self.creds or self.creds.invalid:
            self.flow = client.flow_from_clientsecrets(CREDS_FILE_PATH, SCOPES)
            self.creds = tools.run_flow(self.flow, store)

    def list_files(self) -> List[Tuple[str, str]]:
        try:
            drive_files_json = self.drive.files().list().execute().get('files', [])
            files = []
            for file_json in drive_files_json:
                files.append((file_json.get('id'), file_json.get('name')))
                file_name = file_json['name']
                file_mime_type = file_json['mimeType']
                logger.info(f'{file_name} - {file_mime_type}')
            return files
        except Exception as e:
            logger.exception(e)
            logger.error('Failed to list drive files')

    def get_file_info(self, file_id: str):
        try:
            file_info = self.drive.files().get(fileId=file_id, fields='*').execute()
            logger.debug(file_info)
            return file_info
        except Exception as e:
            logger.exception(e)
            logger.error(f'Failed to get drive file: {file_id}')

    def get_file_permissions(self, file_id: str):
        try:
            file_permissions = self.drive.permissions().list(fileId=file_id, fields='*').execute()
            logger.debug(file_permissions)
            return file_permissions
        except Exception as e:
            logger.exception(e)
            logger.error(f'Failed to get drive file permissions: {file_id}')

    def remove_file_public_permission(self, file_id: str) -> bool:
        try:
            output = self.drive.permissions().delete(fileId=file_id,
                                                     permissionId=PUBLIC_EXPOSURE_PERMISSION_ID).execute()
            if output:
                return False
            else:
                return True
        except Exception as e:
            logger.exception(e)
            logger.error(f'Failed to delete drive file public permissions: {file_id}')

    def get_recent_activity_changes(self):
        try:
            request_body = {"pageSize": ACTIVITY_PAGE_SIZE,
                            "filter": f"detail.action_detail_case:CREATE AND time >= {self.last_activity_check}"}
            all_activity_data = self.drive_activity.activity().query(body=request_body).execute()
            activities = all_activity_data.get('activities')
            next_page_token = all_activity_data.get('nextPageToken')
            while next_page_token:
                request_body = {"pageSize": ACTIVITY_PAGE_SIZE,
                                "filter": f"detail.action_detail_case:CREATE AND time >= {self.last_activity_check}",
                                "pageToken": next_page_token}
                all_activity_data = self.drive_activity.activity().query(body=request_body).execute()
                activities.extend(all_activity_data.get('activities'))
                next_page_token = all_activity_data.get('nextPageToken')

            self.last_activity_check = get_unix_time_in_ms(datetime.datetime.now())
            if activities:
                for activity in activities:
                    if activity.get('primaryActionDetail'):
                        if activity.get('primaryActionDetail').get('create'):
                            self.update_files_permissions()
                            break
            else:
                logger.info("No activities found")
        except HttpError as e:
            logger.exception(e)
            logger.error('Failed to get recent activity')

    def update_files_permissions(self):
        files = self.list_files()
        for file in files:
            file_id, name = file
            permissions = self.get_file_permissions(file_id)
            if is_file_publicly_exposed(file_id, permissions):
                logger.info(f'the file: {file_id} ({name}) is publicly exposed, restricting permissions')
                self.remove_file_public_permission(file_id)
