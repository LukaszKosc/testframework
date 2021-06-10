import logging
import sys


class Logger:
    def __init__(self, name='global', level='DEBUG'):
        self._level_mappings = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARN,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
            }
        self._level = level
        self._name = name
        self.logger = logging.getLogger(self._name)
        self.set_level(level=self._level)
            
    def set_level(self, level):
        self._level = self._level_mappings[level.upper()]
        self.logger.setLevel(level=self._level)

    def get_level(self):
        return self._level
    
    def add_file_handler(self, filepath='example.log'):
        self.logger.addHandler(logging.FileHandler(filename=filepath))

    def add_stdout_handler(self):
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def get_logger(self):
        return self.logger
    
    def Debug(self, msg):
        self.logger.debug(msg=msg)

    def Info(self, msg):
        self.logger.info(msg=msg)


logger = Logger()
logger.add_stdout_handler()
logger.add_file_handler('example.log')