import datetime
import logging
import json

from typing import Dict, Any
from consts import PUBLIC_EXPOSURE_PERMISSION_ID

logger = logging.getLogger(__name__)


def _print_json_output(json_object: Dict):
    logger.debug(json.dumps(json_object, indent=2))


def is_file_publicly_exposed(file_id: str, permissions: Dict[str, Any]) -> bool:
    if not _is_permissions_json(permissions):
        raise ValueError(f'Permissions json or {file_id} is invalid')
    if permissions.get('permissions'):
        for permission in permissions.get('permissions'):
            if permission.get('id') == PUBLIC_EXPOSURE_PERMISSION_ID:
                logger.debug(f"the file {file_id} is publicly exposed")
                return True
    logger.debug(f"the file {file_id} is NOT publicly exposed")
    return False


def _is_permissions_json(data: Dict[str, Any]) -> bool:
    if data.get('kind'):
        if data.get('kind') != 'drive#permissionList':
            return False
    return True


def get_unix_time_in_ms(date: datetime):
    unix_time = int(date.strftime("%s")) * 1000
    return unix_time
