BASE_DRIVE_API_URL = 'https://www.googleapis.com/drive/v3'
PUBLIC_EXPOSURE_PERMISSION_ID = 'anyoneWithLink'
VERIFY = True
ALLOW_REDIRECTS = False
LIST_FILES_PATH = '/files'
FILE_INFO_PATH = '/files/{file_id}'
FILE_PERMISSIONS_PATH = '/files/{file_id}/permissions'
DELETE_FILE_PERMISSION_PATH = '/files/{file_id}/permissions/{public_exposure_permission_id}'
ABOUT_PATH = '/about'
START_PAGE_TOKEN_PATH = '/changes/startPageToken'
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.activity.readonly',
          'https://www.googleapis.com/auth/drive.activity']
DRIVE_SERVICE_NAME = 'drive'
DRIVE_ACTIVITY_SERVICE_NAME = 'driveactivity'
DRIVE_API_VERSION = 'v3'
DRIVE_ACTIVITY_API_VERSION = 'v2'
ACTIVITY_PAGE_SIZE = '100'
ACTIVITY_CHECK_INTERVAL = 30

