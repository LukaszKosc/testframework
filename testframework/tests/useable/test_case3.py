from testframework.engine.base_class import BaseTest
from testframework.engine.web_test import TestWeb
from testframework.libraries.logger import logger

class TestCase3(BaseTest):

    def setup_method(self):
        self.web_handle = TestWeb()

    def test_scenario31(self):
        logger.Info('hello at info level')
        print('some text in {}'.format(self._test_name))
        self.web_handle.run_test()
        logger.Info('cos do pliku')

