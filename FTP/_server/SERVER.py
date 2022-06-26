# Modules ========================
import socket
from os import (system, chdir, listdir, mkdir, rmdir,
                getenv, getpid, getcwd, path, rename)
from threading import Thread


# Global variables ===============
# 1. Server
HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 2002
HOST_ADDRESS = (HOST_IP, HOST_PORT)

# 2. Data
ENCODING = "utf-8"
ROOT_DIR = getenv("USERPROFILE") + path.join("/FTP/server")
SIZE = 1024 * 1024 * 1024  # Default 1GB

# 3. Admin Authentication
ADMIN_ID = "@de-min"
ADMIN_PW = "ftp@STRONG"

# 4. User Authentication
USER_CRED = {
    # user_id: user_password
}

HELP = """Available Commands___________________________________________:
    ?, h             : Help.
    --X              : [❗] STOP the ftp CLIENT and quit.
    
    | USER COMMANDS |
    cd               : Show current directory path.
    cd <path>        : Change directory to <path>.
    dir              : List of files and directories in current directory.
    profile          : Make the current working directory as the client's user directory.
    dl <file> [file] : Download the specified <file>. e.g., path/folder/filename.ext
    ul <file>        : Upload the specified <file>. e.g., path/folder/filename.ext
    pw <user>        : Change the password for the current <user> or client.
    
    | In use:
    cd "D:/Path/to/My Directory"dl "host_file.ext"
    ul "path/to/Local Directory/file_to_be upload.ext"
    
    | ADMIN COMMANDS |
    ADMIN <id> <pass>
    ROOT             : Make the current directory to be as root dir for the FTP server.
    RN <f/d>         : Rename the file specified <file/directory>.
    DEL <f/d>        : Delete the specified <file/directory>.\n"""


# Main Server ====================
def PRIME():
    print("[ INITIALIZING ] Server is initializing. Please wait ...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(HOST_ADDRESS)
    print(f"[ STARTED ] Server started at {HOST_IP}:{HOST_PORT} with PID {getpid()}.")
    server.listen()
    print("[ LISTENING ] Waiting for the incoming connections ...\n")

    while True:
        connection, address = server.accept()
        Thread(target=client, args=(connection, address)).start()


# Client Handling ================
def client(connection, address):
    """
    Commands -> "LINKED", "UNLINED", "OK", "DONE"
    Commands <- "",

    :param connection: Client connection details provided by socket
    :param address: Client connection address provided bu socket
    :return: Perform tasks by communicating with each client through commands and messages (CMD@Message)
    """
    chdir(ROOT_DIR)

    print(f"[ + CONNECTED ] Client connected from {address}.")
    connection.send("LINKED@[ LINKED ] You're now connected with the server.\n"
                    "\n[ W E L C O M E ] Now you can do your tasks by running your commands."
                    "\n[ HINT ] Type '?' and press enter to see available commands anytime.".encode(ENCODING))

    while True:
        # Receives client's commands from their terminal
        client_data = connection.recv(SIZE)

        # [BUG] Uploads a file
        try:
            client_cmd = client_data.decode(ENCODING)
        except Exception as e:
            client_cmd = None
            with open(f"{ROOT_DIR}/__received_file", "wb") as file:
                file.write(client_data)
            connection.send("UL@Sending file name ...".encode(ENCODING))
            while 1:
                __client_data = connection.recv(SIZE).decode(ENCODING)
                print(__client_data)
                rename(f"{ROOT_DIR}/__received_file", f"{ROOT_DIR}/{__client_data}")
                break

        if client_cmd is None:
            pass
        elif client_cmd.lower() in ["h", "?"]:
            # Displays help on users' request
            connection.send(f"OK@{HELP}".encode(ENCODING))
        elif client_cmd == "CD":
            connection.send(f"OK@{getcwd()}".encode(ENCODING))
        elif client_cmd == "DIR":
            connection.send(f"OK@{listdir()}".encode(ENCODING))
        elif client_cmd.split()[0] == "dl":
            # Sends file to the client if exists in the server
            if path.exists(client_cmd.split()[1]):
                with open(client_cmd.split()[1], "rb") as file:
                    print(f"[ > PULL ] '{file.name}' file download request from {address}")
                    # Gets file size as bytes
                    size = connection.sendto(file.read(), address)
                    # Sends file to the client as binary
                    connection.send(file.read(size))
                    print(f"[ = SENT ] '{file.name}' file successfully pushed to {address}")

        elif client_cmd == "--X":
            # Terminates the user thread by sending a message to the client end
            connection.send("UNLINKED@[ UNLINKED ] You're disconnected from the server."
                            "\nSee you again...".encode(ENCODING))
            break

        else:
            # Prints 'invalid command' to the clients' terminal if command not found
            connection.send(f"WRONG@Invalid Command. '{client_cmd}' "
                            f"is not recognized as an internal command.".encode(ENCODING))

    print(f"[ - DISCONNECTED ] Client disconnected from {address}.")


# Execution ======================
if __name__ == '__main__':
    PRIME()
