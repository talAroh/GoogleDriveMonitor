import api_request_wrapper
import logging
import time

from api_client_wrapper import APIClientWrapper
from interactsh_client import InteractshClient
from settings import REST_API_MODE
from consts import ACTIVITY_CHECK_INTERVAL

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    if REST_API_MODE:
        # Print user info
        api_request_wrapper.about()

        # API requests client Example
        # files = api_request_wrapper.list_drive_files()
        # for file in files:
        #     logger.debug(file)
        #     file_id, name = file
        #     permissions = api_request_wrapper.get_file_permissions(file_id)
        #     if api_request_wrapper.is_file_publicly_exposed(file_id, permissions):
        #         logger.info(f'the file: {file_id} ({name}) is publicly exposed, restricting permissions')
        #         api_request_wrapper.delete_file_public_permission(file_id)
        #         permissions = api_request_wrapper.get_file_permissions(file_id)
        #     api_request_wrapper.print_file_info(file_id, permissions)
        # logger.info("Done")

        ic = InteractshClient()
        ic.start_interactsh_client()
        logger.info(f'webhook url: {ic.url}')
        api_request_wrapper.watch_changes(ic.url, "")
        ic.monitor_interactsh_client(api_request_wrapper.update_files_permissions())

    else:
        api_client_wrapper = APIClientWrapper()

        # API client wrapper examples
        # api_client_wrapper.list_files()
        # file_id = '123c82jeyV8mG89B_dwU6GfY6m2S--wqul8h9QuZo67w'
        # api_client_wrapper.get_file_permissions(file_id)

        try:
            while True:  # This loop will prevent the code from reaching the rate limit threshold
                api_client_wrapper.get_recent_activity_changes()
                time.sleep(ACTIVITY_CHECK_INTERVAL)
        except KeyboardInterrupt as e:
            logger.exception(e)
            logger.error("Stopping")


if __name__ == '__main__':
    main()
