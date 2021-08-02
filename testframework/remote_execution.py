from libraries.remote_me import WinRMConnection
from libraries.ssh_me import SSHConnection
from libraries.os_detection import DetectOS

if __name__ == "__main__":
    # host_ip = '192.168.88.128'
    # host = DetectOS(host_ip)
    # if host.host_alive():
    #     print('host {} alive'.format(host))
    #     if host.os() == 'windows':
    #         print(WinRMConnection(host_ip, 'kostek', 'kostek').execute_command("ipconfig"))
    # else:
    #     print('host {} is not alive'.format(host))
    
    host_ip = '192.168.88.138'
    host = DetectOS(host_ip)
    if host.host_alive():
        print('host {} alive'.format(host))
        if host.os() == 'linux':
            print(SSHConnection(host_ip, 'kostek', 'kostek').execute_command("ifconfig"))
    else:
        print('host {} is not alive'.format(host))
    host = DetectOS(host_ip)
    print(host.os())
    # print(SSHConnection('192.168.88.138', 'kostek', 'kostek').execute_command("ip a"))
    # print(DetectOS('192.168.88.138').os())
    # print(DetectOS('192.168.88.1').os())