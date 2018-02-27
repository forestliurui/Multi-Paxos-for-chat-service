import logging
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    # filename='../log/test.log',
                    # filemode='w'
                    stream=sys.stdout
                    )

class MyLogging():
    @staticmethod
    def debug(msg):
        logging.debug(msg)

    @staticmethod
    def info(msg):
        logging.info(msg)

    @staticmethod
    def warning(msg):
        logging.warning(msg)

    @staticmethod
    def error(msg):
        logging.error(msg)

    @staticmethod
    def critical(msg):
        logging.critical(msg)


class FileLogging():
    def __init__(self, log_id):
        # logger1 = logging.getLogger('to_screen')
        # logger1.setLevel(logging.INFO)

        logger2 = logging.getLogger('to_file')
        logger2.setLevel(logging.INFO)

        # ch = logging.StreamHandler()
        log_file = '../log/{}.log'.format(log_id)
        fh = logging.FileHandler(log_file)

        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        # ch.setFormatter(formatter)

        # logger1.addHandler(ch)
        logger2.addHandler(fh)

        # self.screen_logger = logger1
        self.file_logger = logger2

    def debug(self, msg):
        self.file_logger.debug(msg)

    def info(self, msg):
        self.file_logger.info(msg)

    def warning(self, msg):
        self.file_logger.warning(msg)

    def error(self, msg):
        self.file_logger.error(msg)

    def critical(self, msg):
        self.file_logger.critical(msg)
