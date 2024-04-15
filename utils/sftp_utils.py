# --------------------------------------------------------------------------- #
#                                   Import                                    #
# --------------------------------------------------------------------------- #
import time
import paramiko

# --------------------------------------------------------------------------- #
#                               Define functions                              #
# --------------------------------------------------------------------------- #
class SFTP:
    
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
        
        # Connect to the SSH server
        self.transport = paramiko.Transport((self.hostname, self.port))
        self.transport.connect(username=self.username, password=self.password)

        # Create an SFTP session
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        
    def close(self) -> None:
        self.sftp.close()
        self.transport.close()

    def ls(self, remote_directory: str) -> list:
        try:
            files = self.sftp.listdir(remote_directory)
            return files
        except Exception as e:
            print(f"Error: {e}")
            return list()
    
    def putfile(
            self,
            local_filepath: str, 
            remote_filepath: str) -> None:
        for attempt in range(3):
            try:
                self.sftp.put(local_filepath, remote_filepath)
                break
            except Exception as e:
                print(f"Error: {e}")
                if attempt < 2:
                    print(f"Retrying upload {attempt + 1}/3 in 5 seconds...")
                    time.sleep(5)
                else:
                    print("Upload failed after 3 attempts.")
                    break

    def getfile(
            self,
            remote_filepath: str,
            local_filepath: str) -> None:
        for attempt in range(3):
            try:
                self.sftp.get(remote_filepath, local_filepath)
                break
            except Exception as e:
                print(f"Error: {e}")
                if attempt < 2:
                    print(f"Retrying download {attempt + 1}/3 in 5 seconds...")
                    print(f"File: {remote_filepath}")
                    time.sleep(5)
                else:
                    print("Download failed after 3 attempts.")
                    break


if __name__ == '__main__':
    pass