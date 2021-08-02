import socket


class DetectOS:
    def __init__(self, host_ip):
        self._ip = host_ip
        self._sock = None
        self._os = None
        self._check_os()

    def _check_os(self):
        self._os = None
        try:
            if self._detect_os(22):
                self._os = 'linux'
        except ConnectionRefusedError as cre:
            pass

        try:
            if self._detect_os(5985):
                self._os = 'windows'
        except ConnectionRefusedError as cre:
            pass

    def os(self):
        return self._os if self._os else 'No OS'

    def host_alive(self):
        return True if self.os() == 'windows' or self.os() == 'linux' else False

    def _detect_os(self, port):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self._ip, port))
            x = self._sock.send(b"a")
            connected = (x == 1)
            if connected:
                self._sock.close()
            return connected
        except TimeoutError as te:
            return None

        except Exception as e:
            print("General exception:", e)
            return None

    def __str__(self):
        return '({}: {})'.format(self._ip, self.os())
