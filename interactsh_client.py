import re
import json
import logging
from subprocess import Popen, STDOUT, PIPE
from typing import Callable, Any

from consts import (POLL_INTERVAL, INTERACTSH_CLIENT_FULL_PATH, BANNER_LINES, URL_LINE_NUMBER,
                    URL_PATTERN, GOOGLE_DRIVE_API_CHANNEL_HEADER)

logger = logging.getLogger(__name__)


class InteractshClient:

    def __init__(self):
        self.count = 0
        self.command = [INTERACTSH_CLIENT_FULL_PATH, "-duc", "-pi", str(POLL_INTERVAL), "-http-only", "-json", "-v"]
        self.url = None
        self.proc = None

    def start_interactsh_client(self):
        self.count = 0
        self.proc = Popen(self.command, stdout=PIPE, stderr=STDOUT, text=True)
        while line := self.proc.stdout.readline():
            self.count += 1
            if self.count <= BANNER_LINES:
                continue
            elif self.count == URL_LINE_NUMBER:
                matches = re.findall(URL_PATTERN, line)
                if matches:
                    self.url = matches[0]
                    logger.debug(self.url)
                else:
                    raise RuntimeError("Couldn't create an interactsh url")
            else:
                return

    def monitor_interactsh_client(self, callback: Callable[[], Any]):
        try:
            while line := self.proc.stdout.readline():
                logger.debug(line)
                logger.debug('-----')
                try:
                    request_response_dict = json.loads(line)
                    if request_response_dict.get('protocol') == 'http':
                        if GOOGLE_DRIVE_API_CHANNEL_HEADER in request_response_dict.get('raw-response'):
                            # Google Drive API channel request
                            callback()
                except json.JSONDecodeError as e:
                    logger.exception(e)
                    logger.error(f"Couldn't convert {line} to json object")
        except KeyboardInterrupt as e:
            if self.proc:
                self.proc.kill()
