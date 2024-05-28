import logging
import sys


class Logger:
    def __init__(self, log_file="server.log"):
        self.log_file = log_file
        handlers = [logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)]
        logging.basicConfig(handlers=handlers, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


    def log_event(self, message):
        logging.info(message)

    def log_error(self, message):
        logging.error(message)
