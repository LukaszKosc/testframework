from testframework.engine.base_class import BaseTest
from testframework.libraries.logger import logger


class TestSuite42(BaseTest):

    def test_scenario42(self):
        logger.Critical('critical msg2')
        logger.Debug('debug msg3')
