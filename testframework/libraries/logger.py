import atexit
import logging
import sys
import os
from testframework.libraries.config import config


class Logger:
    def __init__(self, name, results_dir, level, FORMAT='%(asctime)-15s %(message)s',
                 save_to_file=True, console=True):
        atexit.register(self.separate_logs)

        self._level_mappings = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
        }
        self.formatter = logging.Formatter(FORMAT)
        self.logger_file_output = results_dir
        self.logger = logging.getLogger(name)
        self.set_level(level)
        self.console_on() if console else self.console_off()

        if save_to_file:
            self.save_to_file_on()

    def set_level(self, level):
        self.logger.setLevel(self._level_mappings[level.upper()])

    def disable_level(self, log_level):
        logging.disable(log_level)

    def enable_level(self):
        logging.disable(logging.NOTSET)

    def turn_on_console(self, turn_on):
        self.console_on() if turn_on in [True, 1, 'y', 'Y', 'yes', 'Yes', 'YES'] else self.console_off()

    def console_on(self):
        if not self.console_status():
            soh = logging.StreamHandler(sys.stdout)
            soh.setFormatter(self.formatter)
            self.logger.addHandler(soh)

    def console_off(self):
        self.get_logger().removeHandler(self.get_logger().handlers[self.get_handlers('stdout')])

    def save_to_file_on(self):
        fh = logging.FileHandler(filename=self.logger_file_output)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

    def save_to_file_off(self):
        self.get_logger().removeHandler(self.get_logger().handlers[self.get_handlers('FileHandler')])

    def get_handlers(self, name):
        if not hasattr(self.logger, 'handlers'):
            return -1
        hndlrs = {}
        for hndlr in self.logger.handlers:
            if 'stdout' in str(hndlr):
                hndlrs['stdout'] = self.get_logger().handlers.index(hndlr)
            if 'FileHandler' in str(hndlr):
                hndlrs['FileHandler'] = self.get_logger().handlers.index(hndlr)
        return hndlrs[name] if 'stdout' in hndlrs else -1

    def console_status(self):
        return True if self.get_handlers('stdout') > -1 else False

    def get_logger(self):
        return self.logger

    def Debug(self, msg):
        self.get_logger().debug(msg='DEBUG: {}'.format(msg))

    def Info(self, msg):
        self.get_logger().info(msg='INFO: {}'.format(msg))

    def Warn(self, msg):
        self.get_logger().warning(msg='WARNING: {}'.format(msg))

    def Critical(self, msg):
        self.get_logger().critical(msg='CRITICAL: {}'.format(msg))

    def separate_logs(self):
        levels = self._level_mappings.keys()
        with open(self.logger_file_output, 'r') as logs_file:
            logs = logs_file.readlines()
        lv = locals()
        for log_level in levels:
            lv['{}_logs'.format(log_level)] = []

        for line in logs:
            for log_level in levels:
                if '{}:'.format(log_level) in line:
                    lv['{}_logs'.format(log_level)].append(line)

        for log_level in levels:
            if lv['{}_logs'.format(log_level)]:
                with open(os.path.join(os.path.dirname(self.logger_file_output), '{}.log'.format(log_level)), 'w') as out:
                    out.writelines(lv['{}_logs'.format(log_level)])
        print('Logs have been generated!')
        for log_level in levels:
            del lv['{}_logs'.format(log_level)]


logger = Logger('info', config['results_dir'], level='DEBUG')
