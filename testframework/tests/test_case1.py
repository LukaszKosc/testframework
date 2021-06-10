import logging
import sys
sys.path.append('../..\\')
sys.path.append('../libraries')
from testframework.tests.base_class import BaseTest
from testframework.libraries.ssh_me import SSHConnection
from testframework.libraries.logging_system import logger


class Helper:
    def __init__(self, x):
        self.x = x
    
    def get_data(self):
        return {'1': self.x}


h = Helper(3)
host_ip = '192.168.88.138'
user = 'kostek'
pswd = 'kostek'
cmds = ['ifconfig', 'ip address', 'python3 -VV']
cmds2 = ['cd ~/ && mkdir -p katalog', 'cd ~/ && ls | grep katalog']


logging_level = 'INFO'
logger.set_level(logging_level)


class TestCase1(BaseTest):
    
    def test_scenerio1(self, xxx=123, args=[123, 12314]):
        try:
            print('my name is: ', self._test_name)
            out = None
            if self.ssh.connected():
                out = self.ssh.execute_commands(cmds)
                logger.Info('cmds: {}'.format(out))
                
            logger.Debug('test_scenerio1')
            assert out is not None, 'cmds are empty'
        except AssertionError as ae:
            print(ae)
            self.Errors.append({'test_name': self._test_name, 'cmd': "{}".format(cmds), 'error': str(ae), 'level': 'Critical'})

    def test_scenerio2(self):
        logger.Info('scenario2')
        out = self.ssh.execute_commands(cmds2)
        logger.Info('out of cmds: {}'.format(out))
        assert out is not None, 'cmds are empty'

    def setup_method(self, value_def_in_setup_method='string debugg', ssh_to=SSHConnection):
        try:
            self.Errors = []
            self.value_def_in_setup_method = value_def_in_setup_method
            logger.Debug('setup_method')
            self.ssh = ssh_to(host_ip, user, pswd)
            assert self.ssh.connected() is True, "Host {} is not connected".format(host_ip)
            print('test can go')
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
