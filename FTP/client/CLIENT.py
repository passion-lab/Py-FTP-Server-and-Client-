# Modules ========================
import socket
from os import system, chdir, listdir, mkdir, rmdir, getenv, path, getcwd

# Global variables ===============
# 1. Server
HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 2002
HOST_ADDRESS = (HOST_IP, HOST_PORT)

# 2. Data
ENCODING = "utf-8"  # Text (message) encoding format
USER_DIR = getenv("USERPROFILE") + path.join("/FTP/client")  # Default user dir
# SIZE = 1024 * 1024 * 1024  # Default 1GB
SIZE = 1024
NAME = None  # Default download data (file) name


# Main Server ====================
def communication():
    global USER_DIR, NAME
    chdir(USER_DIR)

    print("[ STARTING ] The client is starting. Please wait ...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[ STARTED ] Client started.")
    print("[ WAITING ] Waiting for the server to connect ...\n")
    client.connect(HOST_ADDRESS)
    # [+] Have to add user authentication before get connected.

    # Listening server commands and messages in a loop
    while True:
        # Gets server data (for file)
        server_data = client.recv(SIZE)  # [+] SIZE should be dynamic, here it's hardcoded
        # try:
        #     server_cmd, server_msg = server_data[0], server_data[1]
        # except:
        #     server_cmd, server_msg = None, None

        try:
            # Defines server command and message if server data is string
            server_cmd = server_data.decode(ENCODING).split("@")[0]
            server_msg = None
            if len(server_data.decode(ENCODING).split("@")) >= 2:
                server_msg = server_data.decode(ENCODING).split("@")[1]
        except:
            server_cmd = None
            server_msg = None
            with open(f"{USER_DIR}/{NAME}", "wb") as file:
                file.write(server_data)
                print(f"[ DOWNLOADED ] The file '{file.name}' is successfully downloaded.")

        # Displays of message to the client's terminal
        if server_cmd in ["LINKED", "UNLINKED", "OK", "WRONG", "UL"]:
            print(server_msg)
            if server_cmd == "UNLINKED":
                break
            if server_cmd == "UL":
                client.send(NAME.encode(ENCODING))

        # Changes client's terminal prompt for ADMIN privilege or when needed
        _prompt = "$_ "
        if server_cmd == "PROMPT":
            _prompt = f"{server_msg} _prompt"

        # Client's terminal point in a loop
        while 1:
            client_command = input(_prompt).strip()

            # Handles local storage management
            # [+] 
            if client_command in ["dir", "cd", "profile"]:
                if not client_command == "profile":
                    system(client_command)
                else:
                    # Changes client's user directory
                    # global USER_DIR
                    USER_DIR = getcwd()
                    print(f"OK. Now '{getcwd()}' is serving as the server's root directory.\n")
            elif len(client_command.split()) == 2 and client_command.split()[0] == 'cd':
                if path.exists(client_command.split()[1]):
                    chdir(client_command.split()[1])
                else:
                    print(f"Path <{client_command.split()[1]}> doesn't exists.\n"
                          f"Check the case-sensitive path or try another.\n")
            # Regrading file downloads
            elif 2 <= len(client_command.split()) < 4 and client_command.split()[0] == "dl":
                # Changes download filename if specified in 3rd argument
                try:
                    NAME = client_command.split()[2]
                except:
                    NAME = client_command.split()[1]
                # Sends commands and argument to the server
                client.send(client_command.encode(ENCODING))
                break

            # [BUG] Regrading file uploads
            elif 2 <= len(client_command.split()) < 4 and client_command.split()[0] == "ul":
                if path.exists(client_command.split()[1]):
                    try:
                        NAME = client_command.split()[2]
                    except:
                        __path = client_command.split()[1]
                        if __path.find("/") >= 0:
                            NAME = __path.split("/")[-1]
                        elif __path.find("\\") >= 0:
                            NAME = __path.split("\\")[-1]
                        else:
                            NAME = __path
                    with open(client_command.split()[1], "rb") as file:
                        size = client.sendto(file.read(), HOST_ADDRESS)
                        client.send(file.read(size))
                    break

            # Confirms user exit
            elif client_command == "--X":
                _ = input("[ ❗ WARNING ] This will STOP the server and exit.\n"
                          "Are you sure to proceed? [Y/N] ").strip()
                print()
                if _ == "Y":
                    # Sends user logout signal to the server
                    client.send(client_command.encode(ENCODING))
                    break
            # Sends any other commands to the server for operation and response
            else:
                client.send(client_command.encode(ENCODING))
                break

    client.close()


# Execution ======================
if __name__ == '__main__':
    communication()
