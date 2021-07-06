from testframework.engine.base_class import BaseTest
from testframework.libraries.ssh_me import SSHConnection
from testframework.libraries.logger import logger


host_ip = '192.168.88.138'
user = 'user'
pswd = 'pass'
cmds = ['ifconfig', 'ip address', 'python3 -VV']
cmds2 = ['cd ~/ && mkdir -p katalog', 'cd ~/ && ls | grep katalog']


class TestCase1(BaseTest):
    def some_method(self):
        print('cokolwiek')

    def test_scenario2(self):
        logger.Info('scenario2')
        out = self.ssh.execute_commands(cmds2)
        logger.Info('out of cmds: {}'.format(out))
        assert out is not None, 'cmds are empty'

    def setup_method(self, value_def_in_setup_method='string debugg', ssh_to=SSHConnection):
        try:
            self.Errors = []
            self.value_def_in_setup_method = value_def_in_setup_method
            logger.Info('setup_method')
            self.ssh = ssh_to(host_ip, user, pswd)
            assert self.ssh.connected() is True, "Host {} is not connected".format(host_ip)
        except AssertionError as ae:
            print(ae)
            self.Errors.append({'cmd': "ssh {}@{}".format(user, pswd), 'error': str(ae), 'level': 'Blocking'})

    def teardown_method(self):
        logger.Debug('local teardown metod of TestCase1')
        if self.ssh.connected():
            self.ssh.disconnect()
        assert self.ssh.connected() is False, "Host {} is connected".format(host_ip)

    @classmethod
    def setup_class(cls):
        logger.Debug('Debug msg: setup_class: {}'.format(cls.__name__))

    @classmethod
    def teardown_class(cls):
        logger.Debug('{} teardown_class'.format(cls.__name__))
