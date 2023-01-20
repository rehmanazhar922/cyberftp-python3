from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import threading, os, sys, time
from prettytable import PrettyTable


help_content = """
$listusers   To list all users
$adduser     To add users
$rmuser      To remove users
$restart     To restart the server
bye          To exit
exit         To exit
"""

# Create an authorizer 
authorizer = DummyAuthorizer()


# Instantiate a FTP handler class 
handler = FTPHandler
handler.authorizer = authorizer

# Define a customized banner 
handler.banner = "pyftpdlib based ftpd ready."

# Specify a masquerade address and the range of ports to use for 
# passive connections. 
handler.masquerade_address = '1.2.3.4'
handler.passive_ports = range(60000, 65535)

# Instantiate FTP server class and listen on 0.0.0.0:2121 
address = ('', 80)
server = FTPServer(address, handler)

# set a limit for connections 
server.max_cons = 256
server.max_cons_per_ip = 5

# start ftp server 
def background_server():
    server.serve_forever()

ftpserver = threading.Thread(target=background_server)

ftpserver.start()
print("Server running as background task!")

def create_user(user, passwd, permission_type):
    pt = permission_type
    if permission_type == "rw":
        permission_type = "elradfmw"
    elif permission_type == "r":
        permission_type = "elr"

    try:
        os.mkdir(f"users/{user}")
    except:
        pass

    try:
        authorizer.add_user(user, passwd, f"users/{user}", perm=permission_type)
        print(f"Created a User: {user}, Password {passwd}")
        file = open("users.csv", "a")
        file.write(f"\n{user},{passwd},{pt}")
        file.close()
    except:
        print("User creation failed\n\nor\n\nmaybe already exists")

def remove_user(user, passwd, permission_type):
    try:
        os.removedirs(f"users/{user}")
    except:
        pass

    file = open("users.csv", "r")
    data = file.read()
    data = data.replace(f"{user},{passwd},{permission_type}", "")
    file.close()
    file = open("users.csv", "w")
    file.write(data)
    
def list_users():
    try:
        file = open("users.csv", "r")
        data = file.readlines()
        file.close()
        table = PrettyTable()
        table.field_names = ["username", "password", "Permission"]
    
        for line in data:
            if ",r" or ",rw" in line:
                try:
                    line = line.split(",")
                    usr = line[0]
                    pswd = line[1]
                    perms = line[2]
                    try:
                        table.add_row([usr, pswd, perms])
                    except:pass
                except:pass
        print(table)
    except:
        print("No users found on this server see help by 'help'")

def restart():
    time.sleep(5)
    os.system(f"{sys.argv[0]} {sys.argv}")

def restore_users():
    try:
        os.makedirs("users")
    except:
        print("Old users folder exists")

    if os.path.exists("users.csv"):
        file = open("users.csv", "r")
        users = file.readlines()
        for user in users:
            user = user.replace("\n", "")
            user = user.split(",")
            try:
                username = user[0]
                passwd = user[1]
                perm = user[2]
                arguments = (username, passwd, perm)
                create_usr_thread = threading.Thread(target=create_user, args=arguments).start()
            except:
                pass
        file.close()

restore_users()
def server_handling():
    cmd = input("Ftp Shell: ")
    if "$adduser" in cmd:
        creds = cmd.split(" ")
        try:
            user = creds[1]
            passwd = creds[2]
            permission = creds[3]
            arguments = (user, passwd, permission)
            create_usr_thread = threading.Thread(target=create_user, args=arguments).start()
        except:
            print("Syntax : $adduser user passwd r or rw")

    if "$rmuser" in cmd:
        creds = cmd.split(" ")
        try:
            user = creds[1]
            passwd = creds[2]
            permission = creds[3]
            arguments = (user, passwd, permission)
            create_usr_thread = threading.Thread(target=remove_user, args=arguments).start()
            print("User removed from server configs the authentication will be removed after when the server will restarted")
        except:
            print("Syntax : $rmuser user passwd r or rw")

    if "$listusers" in cmd:
        try:
            list_users()
        except:pass

    if "help" in cmd:
        print(help_content)

    if cmd == "exit":
        print("Bye")
        os._exit(0)

    if cmd == "bye":
        print("Bye")
        os._exit(0)

    if cmd == "$restart":
        threading.Thread(target=restart()).start()
        os._exit(0)
    

    server_handling()
server_handling()
