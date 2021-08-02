import atexit
import re
import inspect
from datetime import datetime
from testframework.libraries.logger import logger
from testframework.libraries.timers import get_time_delta
from testframework.libraries.config import config


class BaseTest(object):
    def __init__(self, *args, **kwargs):
        # register what will happen at exit of object
        atexit.register(self.cleanup_basetest)
        # register execution start of test suite
        self._suite_timestamp_start = datetime.now()
        self._suite_timestamp_stop = None
        # if user defined child class class setup
        if hasattr(self.__class__, 'setup_class'):
            self.__class__.setup_class()
        else:
            if hasattr(BaseTest, '_setup_class'):
                BaseTest._setup_class()
        # run all methods matching regex
        members = inspect.getmembers(self)
        method_matcher = re.compile(config['test_regexes']['method_regex'])
        methods_members = [x[0] for x in members if method_matcher.match(x[0]) and callable(x[1])]
        for test in methods_members:
            setattr(self, test, self.wrap_method(getattr(self, test)))
            getattr(self, test)()

    def wrap_method(self, f):
        def wrapper(*args, **kwargs):
            test_timestamp_start = datetime.now()
            stop_test = False
            test_name = f.__name__
            setattr(self, '_test_name', test_name)
            if 'setup_method' in dir(self.__class__):
                if hasattr(self, 'setup_method'):
                    logger.Debug('{}: setup_method - scenario_name: "{}"'.format(self.__class__.__name__, test_name))
                    self.setup_method()
            else:
                if hasattr(BaseTest, '_setup_method'):
                    BaseTest._setup_method(self)
            # if self.Errors has some blocking level errors - test should be stopped
            if hasattr(self, 'Errors'):
                for error in self.Errors:
                    if 'test_name' in error:
                        if error['test_name'] == self._test_name and error['level'] == 'Blocking':
                            stop_test = True
                    if stop_test:
                        logger.Info('Execution of test "{}" omitted, as for '.format(test_name))
                        for error in self.Errors:
                            logger.Info('\r\ncommand: "{}" \r\noccurred error: "{}" '.format(error['cmd'], error['error']))
            if not stop_test:
                #if not hasattr(self, 'Errors') and not self.Errors:
                f(*args, **kwargs)
            if 'teardown_method' in dir(self.__class__):
                if hasattr(self, 'teardown_method'):
                    logger.Debug('{}: teardown_method - scenario_name: "{}"'.format(self.__class__.__name__, test_name))
                    self.teardown_method()
            else:
                if hasattr(BaseTest, '_teardown_method'):
                    BaseTest._teardown_method(self)
            test_timestamp_stop = datetime.now()
            test_delta = get_time_delta(test_timestamp_stop, test_timestamp_start)
            logger.Debug('Test: "{}" duration: {}'.format(test_name, test_delta))
        return wrapper

    def _setup_method(self):
        # logger.Debug('--------- _setup_method of {} class -----------'.format(self.__class__.__name__))
        pass

    def _teardown_method(self):
        # logger.Debug('--------- _teardown_method of {} class -----------'.format(self.__class__.__name__))
        pass

    @classmethod
    def _setup_class(cls):
        # logger.Debug('{} _setup_class'.format(BaseTest.__name__))
        pass

    @classmethod
    def _teardown_class(cls):
        # logger.Debug('{} _teardown_class'.format(BaseTest.__name__))
        pass

    def cleanup_basetest(self):
        if hasattr(self.__class__, 'teardown_class'):
            getattr(self.__class__, 'teardown_class')()
        else:
            if hasattr(BaseTest, '_teardown_class'):
                BaseTest._teardown_class()
        self._suite_timestamp_stop = datetime.now()
        suite_delta = get_time_delta(self._suite_timestamp_stop, self._suite_timestamp_start)
        logger.Debug('Suite: "{}" duration: {}'.format(self.__class__.__name__, suite_delta))

    def __del__(self):
        # if hasattr(self.__class__, 'teardown_class'):
        #     getattr(self.__class__, 'teardown_class')()
        # else:
        #     if hasattr(BaseTest, '_teardown_class'):
        #         BaseTest._teardown_class()
        # if hasattr(self, 'Errors'):
        #     for error_line in self.Errors:
        #         logger.Debug(error_line)
        pass
