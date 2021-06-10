import inspect
from testframework.libraries.logging_system import logger


from __main__ import get_matcher, get_configuration


class BaseTest(object):
    def __init__(self, *args, **kwargs):
        if hasattr(self.__class__, 'setup_class'):
            self.__class__.setup_class()
        else:
            if hasattr(BaseTest, '_setup_class'):
                BaseTest._setup_class()
        members = inspect.getmembers(self)
        method_matcher = get_matcher(get_configuration()['method_regex'])
        methods_members = [x[0] for x in members if method_matcher.match(x[0]) and callable(x[1])]
        for test in methods_members:
            setattr(self, test, self.wrap_method(getattr(self, test)))
            getattr(self, test)()
    
    def wrap_method(self, f):
        def wrapper(*args, **kwargs):
            print('nazwa', f.__name__)
            stop_test = False
            if 'setup_method' in dir(self.__class__):
                if hasattr(self, 'setup_method'):
                    test_name = f.__name__
                    setattr(self, '_test_name', test_name)
    
                    logger.Debug('{}: setup_method - Debug: scenario_name: "{}"'.format(self.__class__.__name__, test_name))
                    self.setup_method()
            else:
                if hasattr(BaseTest, '_setup_method'):
                    logger.Debug('BaseTest: setup_method - Debug: scenario_name: "{}"'.format(test_name))
                    BaseTest._setup_method(self)
            # if self.Errors has some blocking level errors - test should be stopped
            for error in self.Errors:
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
                    logger.Debug('{}: teardown_method - Debug: scenario_name: "{}"'.format(self.__class__.__name__, test_name))
                    self.teardown_method()
            else:
                if hasattr(BaseTest, '_teardown_method'):
                    BaseTest._teardown_method(self)
        return wrapper
    
    def _setup_method(self):
        logger.Debug('--------- _setup_method of {} class -----------'.format(self.__class__.__name__))

    def _teardown_method(self):
        logger.Debug('--------- _teardown_method of {} class -----------'.format(self.__class__.__name__))

    @classmethod
    def _setup_class(cls):
        logger.Debug('{} _setup_class - Debug'.format(BaseTest.__name__))
    
    @classmethod
    def _teardown_class(cls):
        logger.Debug('{} _teardown_class - Debug'.format(BaseTest.__name__))
    
    def __del__(self):
        if hasattr(self.__class__, 'teardown_class'):
            getattr(self.__class__, 'teardown_class')()
        else:
            if hasattr(BaseTest, '_teardown_class'):
                BaseTest._teardown_class()
