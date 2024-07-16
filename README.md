## Description
Google Drive Monitor
This program monitors Google Drive via python the Google Drive API.
In this project I use two clients, one based on requests (REST API),
and the second client uses the `googleapiclient` package

## Prerequisites
- Python 3.10.12 or higher
- A Google Cloud Project
- A Google account with Google Drive enabled


## Setup
- Enabled Google Drive API in Google Cloud
- Configure the OAuth consent screen
- Install the `requirements.txt` file
- Edit the settings.py file with the credentials file/access tokens
- Create an OAuth 2.0 Client IDs (for Desktop app or web app)
  - For the web app client, You need to create an access token using this guide: 
  [OAuth 2.0 Playground](https://developers.google.com/explorer-help/code-samples#curl) 

## Usage
 `python main.py`

## Output Samples
```
# Requests client
20:01:45 - INFO - list_drive_files:
20:01:45 - INFO - the file: 123c82jeyV8mG89B_dwU6GfY6m2S--wqul8h9QuZo67w (test_2) is publicly exposed, restricting permissions
20:01:48 - INFO - File permissions for test_2:
20:01:48 - INFO - 		dfgdfgd sdfsdf (taltal9876543@gmail.com) - owner
20:01:49 - INFO - File permissions for sdfsdfsdf:
20:01:49 - INFO - 		dfgdfgd sdfsdf (taltal9876543@gmail.com) - owner
20:01:50 - INFO - File permissions for test_file:
20:01:50 - INFO - 		tal4884 (tal4884@gmail.com) - reader
20:01:50 - INFO - 		dfgdfgd sdfsdf (taltal9876543@gmail.com) - owner
20:01:51 - INFO - File permissions for c:
20:01:51 - INFO - 		tal4884 (tal4884@gmail.com) - reader
20:01:51 - INFO - 		dfgdfgd sdfsdf (taltal9876543@gmail.com) - owner
20:01:52 - INFO - File permissions for test_folder:
20:01:52 - INFO - 		tal4884 (tal4884@gmail.com) - reader
20:01:52 - INFO - 		dfgdfgd sdfsdf (taltal9876543@gmail.com) - owner
20:01:52 - INFO - Done

Python API Client
20:03:06 - INFO - file_cache is only supported with oauth2client<4.0.0
20:03:06 - INFO - file_cache is only supported with oauth2client<4.0.0
20:03:06 - INFO - Refreshing due to a 401 (attempt 1/2)
20:03:06 - INFO - Refreshing access_token
20:03:07 - INFO - test_2 - application/vnd.google-apps.document
20:03:07 - INFO - sdfsdfsdf - application/vnd.google-apps.document
20:03:07 - INFO - test_file - application/vnd.google-apps.document
20:03:07 - INFO - c - application/vnd.google-apps.document
20:03:07 - INFO - test_folder - application/vnd.google-apps.folder
```

## Issues
- The `get_recent_activity_changes` func is not tested in the code because of permission issues.
  But I did test the API arguments in https://developers.google.com/drive/activity/v2/reference/rest/v2/activity/query
- The `watch_changes` func is not tested and fully implemented.
  I've used an internet web hook service for testing and got messages through it,
  the message only indicated that a change was made in the drive so I had to search for the files with `update_files_permissions` and updated the new files
  the messages looked like:
  ```
  accept-encoding gzip, deflate, br
  user-agent  APIs-Google; (+https://developers.google.com/webmasters/APIs-Google.html)
  content-length  0
  x-goog-channel-token    
  x-goog-resource-uri https://content.googleapis.com/drive/v3/changes?alt=json&fields=*&includeItemsFromAllDrives=true&pageToken=56&restrictToMyDrive=true&supportsAllDrives=true
  x-goog-resource-id  KoUdK0_A4kK5WF1A_XEMryMfHBU
  x-goog-message-number   16783561
  x-goog-resource-state   change
  x-goog-channel-expiration   Thu, 11 Jul 2024 12:13:19 GMT
  x-goog-channel-id   7468f0bc-03b4-4ec5-b893-ae6c9ffa958c
  accept  */*
  host    webhook.site
  content-type
  ```

## Default sharing settings
I couldn't find the default sharing settings of files in the Google account.
I searched all the Object in [Google Drive API](https://developers.google.com/drive/api/reference/rest/v3)
But I think that if this setting can be found it will require the existence of shared drives (Because in the personal 
local drive the default setting is restricted and it can't be changed)

## Attack Surface
- The credentials and access tokens/api keys are stored as plaintext be default, and they can be stolen.
- It requires many Oauth client types in order to use the different types of applications. 
  This cause for a lot of accounts that are hard to manage.
  also these accounts tokens are never expires/rotated.
- When using the `changes` API, I've noticed that the resourceId in the channel object which 
  identifies the resource being watched on this channel Is ignored and other files can be watched too,
  Leading to a possible information leakage.