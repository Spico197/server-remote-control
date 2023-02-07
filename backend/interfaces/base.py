import logging
logging.getLogger("paramiko").setLevel(logging.WARNING)

from paramiko import AutoAddPolicy
from paramiko.client import SSHClient
from paramiko.ssh_exception import AuthenticationException, SSHException


class ManageAPI:
    def login(self):
        raise NotImplementedError

    def get_power_status(self) -> int:
        raise NotImplementedError

    def power_off(self):
        raise NotImplementedError

    def power_reset(self):
        raise NotImplementedError

    def power_on(self):
        raise NotImplementedError


class ServerDownException(SSHException):
    pass


class ServerSSH:
    def __init__(
        self, ssh_ip, ssh_username, ssh_password, ssh_port=22, ssh_timeout=10.0
    ) -> None:
        self.ssh_ip = ssh_ip
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ssh_timeout = ssh_timeout

    def ssh_ping(self):
        client = SSHClient()
        try:
            client.load_system_host_keys()
            client.connect(
                self.ssh_ip,
                port=self.ssh_port,
                username=self.ssh_username,
                password=self.ssh_password,
                timeout=self.ssh_timeout,
            )
            return True
        except AuthenticationException:
            # even authentication is failed, the server is still alive
            return True
        except KeyboardInterrupt:
            raise NotImplementedError
        except (EOFError, SSHException, Exception) as err:
            return False
        finally:
            client.close()

    def ssh_run(self, command: str, timeout=10.0):
        client = SSHClient()
        try:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(
                self.ssh_ip,
                port=self.ssh_port,
                username=self.ssh_username,
                password=self.ssh_password,
                timeout=self.ssh_timeout,
            )
            _, sout, serr = client.exec_command(command, timeout=timeout)
            return (sout.readlines(), serr.readlines())
        except AuthenticationException:
            raise AuthenticationException
        except KeyboardInterrupt:
            raise NotImplementedError
        except (EOFError, SSHException, Exception):
            raise ServerDownException
        finally:
            client.close()

    def get_gpu_num(self, timeout=10.0):
        sout, serr = self.ssh_run("nvidia-smi -L | wc -l", timeout=timeout)
        if "command not found" in sout:
            return 0
        else:
            return int(sout[0].strip())
