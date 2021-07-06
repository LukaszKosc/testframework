from testframework.engine.base_class import BaseTest
from testframework.libraries.ssh_me import SSHConnection
from testframework.libraries.logger import logger

host_ip = '192.168.88.138'
cmds = ['ifconfig', 'ip address', 'python3 -VV']
cmds2 = ['cd ~/ && mkdir -p katalog', 'cd ~/ && ls | grep katalog']


class TestCase2(BaseTest):

    def test_scenerio21(self, xxx=123, args=[123, 12314]):
        if self.ssh:
            out = self.ssh.execute_commands(cmds)
        self.value_set_in_test_scenario1 = xxx
        print('self.value_def_in_setup_method', self.value_def_in_setup_method)
        print('self.value_set_in_test_scenario1', self.value_set_in_test_scenario1)
        print(xxx)
        print(args)
        logger.Info('cmds: {}'.format(out))
        logger.Debug('debug tekst')

