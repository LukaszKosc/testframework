import socket
import paramiko
import traceback
from testframework.libraries.logger import logger


class SSHConnection:
    def __init__(self, hostname, username, password, timeout=None):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._timeout = None
        self._ssh_connection = None
        if timeout:
            self._timeout = timeout
        if self.is_host_alive():
            self._ssh_connection = self._connect()

    def is_host_alive(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self._hostname, 22))
            x = self._sock.send(b"a")
            connected = (x == 1)
            if connected:
                self._sock.close()
            return connected

        except TimeoutError as e:
            logger.Debug('TimeoutError: {}'.format(e))
            logger.Debug(traceback.print_exc())
            return False

        except Exception as e:
            return False

    def connected(self):
        if self._ssh_connection:
            if self._ssh_connection.get_transport():
                if self._ssh_connection.get_transport().is_active():
                    return True
        return False

    def _connect(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                if self._timeout:
                    ssh.connect(self._hostname, username=self._username, password=self._password, timeout=self._timeout)
                else:
                    ssh.connect(self._hostname, username=self._username, password=self._password)
                if ssh.get_transport().is_active():
                    print("Connected to {}".format(self._hostname))

            except TimeoutError as e:
                print("TimeoutError(caught):", e)
                ssh = None
        except paramiko.AuthenticationException:
            print("Failed to connect to {} due to wrong username/password".format(self._hostname))
            ssh = None

        except Exception as e:
            print(e)
            ssh = None

        return ssh

    def execute_command(self, command):
        try:
            command = command.strip()
            std_in, std_out, std_err = self._ssh_connection.exec_command(command)
            std_out, std_err = std_out.readlines(), std_err.readlines()
            return ''.join(std_out), ''.join(std_err)

        except Exception as e:
            print('exception', e)
            return '', str(e)

    def execute_commands(self, commands):
        replies = {}
        if self.connected():
            commands = commands.split('\r\n') if isinstance(commands, str) else commands
            for cmd in commands:
                stdout, stderr = self.execute_command(cmd)
                if not stderr:
                    replies[cmd] = stdout
        return replies

    def disconnect(self):
        try:
            if self.connected():
                self._ssh_connection.close()

        except Exception as e:
            print(e)

        finally:
            if not self.connected():
                self._ssh_connection = None

    def __del__(self):
        pass
