from testframework.engine.base_class import BaseTest
from testframework.libraries.logger import logger


class TestCase12(BaseTest):

    def test_scenario12(self):
        logger.Critical('critical msg2')
        logger.Debug('debug msg3')
