# import winrm
#
# sess = winrm.Session('http://192.168.88.128', auth=('kostek', 'kostek'))
# cmds = ["ipconfig /all", "ipconfig /flushdns", "nslookup wp.pl"]
#
# def run_command(cmdline):
#     print('----- running cmd: {} ------'.format(cmdline))
#     if " " in cmdline:
#         cmd_parts = cmdline.split()
#         cmd = cmd_parts[0]
#         args = cmd_parts[1:]
#     result = sess.run_cmd(cmd, args)
#     print('---- result: {} -----'.format(result))
#
#     print(result.std_err)  # .decode("utf-8"):
#     print(result.std_out)
#
#
# def run_ps(cmd):
#     result = sess.run_ps(cmd)
#     print(result)
#     print(result.std_out)
#     print(result.std_err)
#
#
# ps_cmds = ["""$computerName=$Host
# echo $computerName
# """, """hostname"""]
#
# for cmd in cmds:
#     run_command(cmd)
#
# # for cmd in ps_cmds:
# #    run_ps(cmd)
import winrm


class WinRMConnection:
    def __init__(self, hostname, username, password, timeout=None):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._timeout = None
        # if timeout:
        #     self._timeout = timeout
        self._connection = self._connect()

    def get_connection(self):
        if self._connection:
            return self._connection
        return None

    def _connect(self):
        try:
            try:
                if self._timeout:
                    connection_session = winrm.Session('http://{}'.format(self._hostname),
                                                       auth=(self._username, self._password),
                                                       read_timeout_sec=self._timeout + 5,
                                                       operation_timeout_sec=self._timeout)
                else:
                    connection_session = winrm.Session('http://{}'.format(self._hostname),
                                                       auth=(self._username, self._password))
                    
            except TimeoutError as e:
                print("TimeoutError(caught):", e)
                connection_session = None
            
        except Exception as e:
            print(e.message)
            connection_session = None

        if connection_session:
            print("Connected to {}".format(self._hostname))
        else:
            print("Did not connect to {}".format(self._hostname))
            return
        return connection_session

    def execute_command(self, command, method='cmd'):
        try:
            if method == 'cmd':
                response = self._run_cmd(command)
            elif method == 'ps':
                response = self._run_ps(command)
            else:
                return None, None, None

        except Exception as e:
            print(e.message)

        return None, response.std_out, response.std_err

    def _run_cmd(self, cmdline):
        try:
            print('----- running cmd: {} ------'.format(cmdline))
            if " " in cmdline:
                cmd_parts = cmdline.split()
                cmd_core = cmd_parts[0]
                cmd_args = cmd_parts[1:]
                result = self.get_connection().run_cmd(cmd_core, cmd_args)
            else:
                result = self.get_connection().run_cmd(cmdline)
            return result
        except Exception as e:
            print(e)
            return None

    def _run_ps(self, cmdline):
        try:
            print('----- running cmd(ps): {} ------'.format(cmdline))

            result = self.get_connection().run_ps(cmdline)
            return result
        except Exception as e:
            print(e)
            return None

    def disconnect(self):
        try:
            if self._connection:
                self._connection = None
        except Exception as e:
            print(e.message)
        finally:
            self._connection = None

    def __del__(self):
        print('Disconnecting from host "{}"'.format(self._hostname))
        self.disconnect()


if __name__ == "__main__":
    print(WinRMConnection('192.168.88.128', 'kostek', 'kostek').execute_command("ipconfig"))