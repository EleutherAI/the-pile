import logging
import time
from datetime import timedelta

from tqdm import tqdm

class LogFormatter():

    def __init__(self):
        self.start_time = time.time()

    def format(self, record):
        elapsed_seconds = round(record.created - self.start_time)

        prefix = "%s - %s - %s" % (
            record.levelname,
            time.strftime('%x %X'),
            timedelta(seconds=elapsed_seconds)
        )
        message = record.getMessage()
        message = message.replace('\n', '\n' + ' ' * (len(prefix) + 3))
        return "%s - %s" % (prefix, message) if message else ''

    def reset_time(self):
        self.start_time = time.time()

def setup_logger(filepath=None, to_console=True, formatter=LogFormatter()):

    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    logger.handlers = []    

    # create file handler
    if filepath is not None:
        file_handler = logging.FileHandler(filepath, "a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # create console handler
    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

class ChildProcessHandler(logging.StreamHandler):
    def __init__(self, message_queue):
        self.message_queue = message_queue
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        self.message_queue.put(record)

def setup_logger_child_process(message_queue):
    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    logger.handlers = []

    # create queue handler
    child_process_handler = ChildProcessHandler(message_queue)
    child_process_handler.setLevel(logging.INFO)
    logger.addHandler(child_process_handler)

class TqdmHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg)

def setup_logger_tqdm(filepath=None, formatter=LogFormatter()):

    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    logger.handlers = []    

    # create file handler
    if filepath is not None:
        file_handler = logging.FileHandler(filepath, "a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # create tqdm handler
    tqdm_handler = TqdmHandler()
    tqdm_handler.setLevel(logging.INFO)
    tqdm_handler.setFormatter(formatter)
    logger.addHandler(tqdm_handler)