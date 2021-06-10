# import logging
# import sys
# sys.path.append('../..\\')
# sys.path.append('../libraries')
# from testframework.tests.base_class import BaseTest
# from testframework.libraries.ssh_me import SSHConnection
# from testframework.libraries.logging_system import logger
#
#
# class Helper:
#     def __init__(self, x):
#         self.x = x
#
#     def get_data(self):
#         return {'1': self.x}
#
#
# h = Helper(3)
# print(h.get_data())
# host_ip = '192.168.88.138'
# cmds = ['ifconfig', 'ip address', 'python3 -VV']
# cmds2 = ['cd ~/ && mkdir -p katalog', 'cd ~/ && ls | grep katalog']
#
#
# logging_level = 'DEBUG'
# logger.set_level(logging_level)
#
#
# class TestCase1(BaseTest):
#
#     def test_scenerio21(self, xxx=123, args=[123, 12314]):
#         if self.ssh:
#             out = self.ssh.execute_commands(cmds)
#         self.value_set_in_test_scenario1 = xxx
#         print('self.value_def_in_setup_method', self.value_def_in_setup_method)
#         print('self.value_set_in_test_scenario1', self.value_set_in_test_scenario1)
#         print(xxx)
#         print(args)
#         logger.Info('cmds: {}'.format(out))
#         logger.Debug('debug tekst')
#
#     def test_scenerio22(self):
#         print('scenario2')
#         print('self.value_set_in_test_scenario1', self.value_set_in_test_scenario1)
#         if self.ssh:
#             out = self.ssh.execute_commands(cmds2)
#         print(out)
#
#     def setup_method(self, value_def_in_setup_method='string debugg', ssh_to=SSHConnection):
#         logger.Info('info aaaa')
#         self.value_def_in_setup_method = value_def_in_setup_method
#         logger.Debug('debug tekst')
#         # self.ssh = SSHConnection(host_ip, 'kostek', 'kostek')
#         self.ssh = ssh_to(host_ip, 'kostek', 'kostek')
#
#     def teardown_method(self):
#         logger.Debug('local teardown metod of TestCase1')
#         if self.ssh:
#             self.ssh.disconnect()
#
#     @classmethod
#     def setup_class(cls):
#         logger.Debug('Debug msg: setup_class: {}'.format(cls.__name__))
#
#     @classmethod
#     def teardown_class(cls):
#         logger.Debug('{} teardown_class'.format(cls.__name__))
