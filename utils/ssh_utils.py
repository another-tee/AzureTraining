# --------------------------------------------------------------------------- #
#                                   Import                                    #
# --------------------------------------------------------------------------- #
import paramiko

# --------------------------------------------------------------------------- #
#                               Define functions                              #
# --------------------------------------------------------------------------- #
class SSH:
    
    def __init__(
            self, 
            public_ip: str,
            port: int,
            username: str,
            password: str) -> None:
        
        self.hostname = public_ip
        self.port = port
        self.username = username
        self.password = password
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh_client.connect(
                self.hostname, 
                username=self.username, 
                password=self.password
            )
        except Exception as e:
            print(e)
        
    def close(self) -> None:
        self.ssh_client.close()

    def exec(self, command) -> None:
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        for line in stdout:
            print(line.strip())


if __name__ == '__main__':
    pass