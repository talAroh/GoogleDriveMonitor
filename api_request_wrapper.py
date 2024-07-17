import requests
import logging
import uuid
import datetime

from typing import Dict, List, Any, Tuple
from consts import (BASE_DRIVE_API_URL, PUBLIC_EXPOSURE_PERMISSION_ID, VERIFY, ALLOW_REDIRECTS,
                    LIST_FILES_PATH, FILE_INFO_PATH, FILE_PERMISSIONS_PATH, DELETE_FILE_PERMISSION_PATH, ABOUT_PATH,
                    START_PAGE_TOKEN_PATH)
from settings import API_KEY, ACCESS_TOKEN
from models import HTTPMethod
from utils import _print_json_output, _is_permissions_json, is_file_publicly_exposed, get_unix_time_in_ms

logger = logging.getLogger(__name__)


def _send_drive_api_request(http_method: HTTPMethod,
                            path: str,
                            query_params: Dict[str, Any] = None,
                            body: Dict[str, Any] = None,
                            base_url: str = BASE_DRIVE_API_URL,
                            api_key: str = API_KEY,
                            access_token: str = ACCESS_TOKEN) -> requests.Response:
    path = path if path.startswith('/') else '/' + path
    url = base_url + path
    if not query_params:
        query_params = {}
    query_params["key"] = api_key
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    try:
        response = requests.request(method=http_method.value,
                                    url=url,
                                    params=query_params,
                                    headers=headers,
                                    verify=VERIFY,
                                    allow_redirects=ALLOW_REDIRECTS,
                                    json=body)
        if 200 <= response.status_code <= 299:
            logger.debug(f"Got {response.status_code} for url {url}")
            return response
        else:
            logger.error(f"API request to {response.request.url} failed with error {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        logger.error(f"Failed to send an API request to {url}")


def list_drive_files() -> List[Tuple[str, str]]:
    response = _send_drive_api_request(HTTPMethod.GET, LIST_FILES_PATH, query_params={"fields": "*"})
    logger.info("list_drive_files:")
    drive_files_json = response.json()
    files = []
    if drive_files_json.get('files'):
        for file_json in drive_files_json.get('files'):
            files.append((file_json.get('id'), file_json.get('name')))
    _print_json_output(drive_files_json)
    return files


def _get_file_info(file_id: str) -> Dict[str, Any]:
    response = _send_drive_api_request(HTTPMethod.GET, FILE_INFO_PATH.format(file_id=file_id),
                                       query_params={"fields": "*"})
    logger.debug("file info:")
    file_info = response.json()
    _print_json_output(file_info)
    return file_info


def get_file_permissions(file_id: str) -> Dict[str, Any]:
    response = _send_drive_api_request(http_method=HTTPMethod.GET, path=FILE_PERMISSIONS_PATH.format(file_id=file_id),
                                       query_params={"fields": "*"})
    logger.debug(f"file permissions of {file_id}")
    permissions = response.json()
    _print_json_output(permissions)
    return permissions


def delete_file_public_permission(file_id: str) -> bool:
    response = _send_drive_api_request(HTTPMethod.DELETE,
                                       DELETE_FILE_PERMISSION_PATH.format(file_id=file_id,
                                                                          public_exposure_permission_id=
                                                                          PUBLIC_EXPOSURE_PERMISSION_ID))
    if response.status_code == 204:
        logger.debug(f'public access deleted successfully for file {file_id}')
        return True
    else:
        logger.error(f'Failed to delete public access to file: {file_id}')
        return False


def about() -> Dict[str, Any]:
    response = _send_drive_api_request(HTTPMethod.GET, ABOUT_PATH, query_params={"fields": "*"})
    logger.debug("User info:")
    file_info = response.json()
    _print_json_output(file_info)
    return response.json()


def print_file_info(file_id: str, permissions: Dict[str, Any]):
    if not _is_permissions_json(permissions):
        raise ValueError(f'Permissions json or {file_id} is invalid')
    file_info = _get_file_info(file_id)
    file_display_name = file_info.get('name', file_id)
    logger.info(f'File permissions for {file_display_name}:')
    if permissions.get('permissions'):
        for permission in permissions.get('permissions'):
            email = permission.get('emailAddress')
            role = permission.get('role')
            display_name = permission.get('displayName')
            logger.info(f'\t\t{display_name} ({email}) - {role}')


def _create_channel_object(web_hook_address: str, resource_id: str,
                           resource_uri: str = "https://www.googleapis.com/drive/v3/files") -> Dict[str, Any]:
    tomorrow = datetime.date.today() + datetime.timedelta(1)
    unix_time = get_unix_time_in_ms(tomorrow)
    channel_dict = {"payload": False,
                    "id": str(uuid.uuid4()),
                    "resourceId": resource_id,  # For Example: 1zXdxl6ib4CN3Gto75ZeR0rMwqgSFOi6Tbsvxt_TJSZ0 (file id)
                    "resourceUri": resource_uri,
                    "token": "",
                    "expiration": f"{unix_time}",
                    "type": "webhook",
                    "address": web_hook_address,
                    "params": {},
                    "kind": "api#channel"}
    return channel_dict


def _get_changes_start_page_token() -> str:
    response = _send_drive_api_request(HTTPMethod.GET, START_PAGE_TOKEN_PATH, query_params={"fields": "*"})
    logger.debug("getting start page token:")
    page_token_info = response.json()
    return page_token_info.get('startPageToken')


def watch_changes(web_hook_address: str, resource_id: str, resource_uri: str = None):
    if resource_uri:
        channel = _create_channel_object(web_hook_address, resource_id, resource_uri)
    else:
        channel = _create_channel_object(web_hook_address, resource_id)
    start_page_token = _get_changes_start_page_token()
    response = _send_drive_api_request(HTTPMethod.POST, "/changes/watch",
                                       query_params={"pageToken": start_page_token},
                                       body=channel)
    if response.status_code == 200:
        logger.info('Changes watching API request succeeded')
    else:
        logger.error(f'Failed to create a changes watch')


def update_files_permissions():
    files = list_drive_files()
    for file in files:
        logger.debug(file)
        file_id, name = file
        permissions = get_file_permissions(file_id)
        if is_file_publicly_exposed(file_id, permissions):
            logger.info(f'the file: {file_id} ({name}) is publicly exposed, restricting permissions')
            delete_file_public_permission(file_id)
