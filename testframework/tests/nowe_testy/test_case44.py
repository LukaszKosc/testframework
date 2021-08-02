from testframework.engine.base_class import BaseTest
from testframework.libraries.logger import logger


class TestSuite44(BaseTest):

    def test_scenario43(self):
        logger.Critical('critical msg2')
        logger.Debug('debug msg3')

    def test_scenario44(self):
        logger.Critical('critical msg2')
        logger.Debug('debug msg3')
