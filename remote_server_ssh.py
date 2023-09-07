import pysftp
import argparse
import os
import sys
import subprocess
import time
from colorama import Fore, Style, init
import getpass
from tqdm import tqdm

def clear_terminal():
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')

clear_terminal()

##################################################################################################################
# WARNING ! YOU NEED TO CORECTLY ENTER VERY INFORMATION HERE OR THE SCRIPT WILL NOT WORK AND YOU'LL GET AN ERROR #
##################################################################################################################

# SSH Informations
SSH_HOST = 'IP Adress of the server' # ip server
SSH_USERNAME = 'Session username of the server' # User
SSH_PORT = 22  # default ssh port


# Default local path
default_local_path = r'Your default path without the ("")'

##################################################################################################################

# Remplacez ces lignes dans la fonction login()
def login():
    global SSH_PASSWORD
    login_file_path = os.path.join(os.path.dirname(__file__), "login")
    try:
        with open(login_file_path, "r") as password_file:
            SSH_PASSWORD = password_file.read().strip()
    except FileNotFoundError:
        SSH_PASSWORD = getpass.getpass("Password: ")

    while not check_ssh_connection():
        print("")
        print(f"{Fore.RED}Login failed: Incorrect credential or the server is unreachable{Style.RESET_ALL}")
        print("")
        SSH_PASSWORD = getpass.getpass("Password: ")


# Password
print("")
print("You need a password to connect to", SSH_HOST)
print("")
print("Username:", SSH_USERNAME)

print("")

# Etat de la connection
connected = False

# Ping
ping_time = 0

# Durée maximale autorisée pour la connexion en millisecondes
MAX_CONNECTION_TIME = 2500

def check_ssh_connection():
    global connected
    global ping_time

    try:
        ping_command = f"ping -n 1 {SSH_HOST}"  
        start_time = time.time()
        result = subprocess.run(ping_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end_time = time.time()
        ping_time = round((end_time - start_time) * 1000)  # en millisecondes

        if "TTL=" in result.stdout:
            with pysftp.Connection(SSH_HOST, username=SSH_USERNAME, password=SSH_PASSWORD, port=SSH_PORT) as sftp:
                connected = True
                return True
        else:
            connected = False
            return False

    except Exception as e:
        print(f"{Fore.RED}Failed to connect with SSH: {str(e)}{Style.RESET_ALL}")
        connected = False
        return False

def complete_local_path(local_path, default_path):
    if local_path.startswith("/"):
        return default_path + local_path[1:]
    return local_path

def start_ssh_shell():
    ssh_command = f"ssh {SSH_USERNAME}@{SSH_HOST} -p {SSH_PORT}"
    
    try:
        subprocess.run(ssh_command, shell=True)
    except Exception as e:
        print(f"{Fore.RED}Error while trying to start an SSH shell command prompt: {str(e)}{Style.RESET_ALL}")

def ping_host():
    global ping_time

    try:
        ping_command = f"ping -n 1 {SSH_HOST}"
        start_time = time.time()
        result = subprocess.run(ping_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end_time = time.time()
        ping_time = round((end_time - start_time) * 1000) # conversion millisecondes

    except Exception as e:
        print(f"{Fore.RED}Ping failed: {str(e)}{Style.RESET_ALL}")

def ssh_transfer(command, local_path, remote_path):
    global connected

    if command == "status":
        ping_host()
        if connected:
            print("Status: ", end='')
            print(f"{Fore.GREEN}Connected{Style.RESET_ALL} with {ping_time} ms")
        else:
            print("Status: ", end='')

        return

    try:
        with pysftp.Connection(SSH_HOST, username=SSH_USERNAME, password=SSH_PASSWORD, port=SSH_PORT) as sftp:
            if command == "get":
                if os.path.isdir(local_path):
                    remote_files = sftp.listdir(remote_path)
                    for file in remote_files:
                        remote_file = os.path.join(remote_path, file)
                        local_file = os.path.join(local_path, file)
                        sftp.get(remote_file, local_file)
                        print(f"Downloading {file} and saving to {local_file}")
                else:
                    sftp.get(remote_path, local_path)
                    print(f"Downloading {os.path.basename(remote_path)} and saving to {local_path}")
                    
            elif command == "send":
                if local_path is None:
                    print(f"{Fore.YELLOW}You need to provide a local path to use {Fore.GREEN}send{Style.RESET_ALL}")
                    return
                if os.path.isdir(local_path):
                    print(f"{Fore.YELLOW}Sending entire folders using 'send' is not supported. Use 'send-all' for that.{Style.RESET_ALL}")
                    return
                try:
                    sftp.put(local_path, remote_path)
                    print(f"Sending {os.path.basename(local_path)} to {remote_path}")
                except Exception as e:
                    print(f"{Fore.RED}Failed to send: {str(e)}{Style.RESET_ALL}")

            elif command == "del":
                sftp.remove(remote_path)
                print(f"{remote_path} deleted")

            elif command == "ls":
                remote_items = sftp.listdir(remote_path)
                print("")
                print(f"########## Listing {remote_path} ##########")
                print("")
                for item in remote_items:
                    print(item)
                print("")
                print("########## END ##########")

            elif command == "mkdir":
                sftp.mkdir(remote_path)
                print(f"Folder {remote_path} created on the server")

            # Commande get-all 
            elif command == "get-all":
                if not os.path.exists(local_path):
                    os.makedirs(local_path)
                remote_path = remote_path.rstrip('/')  # Remove trailing slash if present
                sftp.get_d(remote_path, local_path)
                print(f"Downloading entire folder {remote_path} and saving to {local_path}")
                # Ajouter cette boucle pour afficher les noms des fichiers téléchargés
                for root, _, files in os.walk(local_path):
                    for file in files:
                        print(f"Downloaded {file}")

            elif command == "send-all":
                if not os.path.exists(local_path):
                    os.makedirs(local_path)
                for root, _, files in os.walk(local_path):
                    remote_dir = os.path.join(remote_path, os.path.relpath(root, local_path))
                    for file in files:
                        local_file = os.path.join(root, file)
                        remote_file = os.path.join(remote_dir, file).replace("\\", "/")  # Formatage correct du chemin
                        sftp.put(local_file, remote_file)
                        print(f"Sending {file} to {remote_file}")
            else:
                print(f"{Fore.YELLOW}Invalid command. Use {Fore.GREEN}help{Fore.YELLOW} for help{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")



def print_banner():
    clear_terminal()
    banner = '''
   _____   _____     _____ _____ _    _ 
  |  __ \ / ____|   / ____/ ____| |  | |
  | |__) | (___    | (___| (___ | |__| |
  |  _  / \___ \    \___ \____ \|  __  |
  | | \ \ ____) |   ____) |___) | |  | |
  |_|  \_\_____/   |_____/_____/|_|  |_|
                                       
  Made by Truitekifile - ver 1.2.0
  https://github.com/Truitekifile/
    '''
    print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")

def print_status():
    global connected
    global ping_time
    status_text = "Connected" if connected else "Disconnected"
    status_color = Fore.GREEN if connected else Fore.RED
    if status_text == "Connected":
        print(f"Status: {status_color}{status_text}{Style.RESET_ALL} with {ping_time} ms \n")

    else:
        print(f"Status: {status_color}{status_text}{Style.RESET_ALL}\n")
        print("")
        print(f"You are not connected to the SSH server. Use {Fore.GREEN}status{Style.RESET_ALL} to check the connection to the server. You may also have provided incorrect login information.")
        print("")

def print_help():
    command_color = Fore.GREEN
    print(f"{command_color}Available commands:{Style.RESET_ALL}")
    print("")
    print(f"  {command_color}get{Style.RESET_ALL} <remote_path> [local_path]: Download a file or a folder from the server")
    print(f"  {command_color}send{Style.RESET_ALL} <local_path> [remote_path]: Send a file or a folder to the server")
    print(f"  {command_color}del{Style.RESET_ALL} <remote_path>: Delete a file or a folder on the server")
    print(f"  {command_color}ls{Style.RESET_ALL} <remote_path>: List the contents of <remote_path> on the server")
    print(f"  {command_color}mkdir{Style.RESET_ALL} <remote_path>: Create a folder on the server")
    print(f"  {command_color}status{Style.RESET_ALL}: Check SSH connection to the server")
    print(f"  {command_color}shell{Style.RESET_ALL}: Start a shell connected to the server")
    print(f"  {command_color}get-all{Style.RESET_ALL} <remote_path> [local_path]: Download the entire contents of a folder from the server")
    print(f"  {command_color}send-all{Style.RESET_ALL} <local_path> [remote_path]: Send the entire contents of a folder to the server")
    print(f"  {command_color}help{Style.RESET_ALL}: Print help")
    print(f"  {command_color}exit{Style.RESET_ALL}: Exit the tool")




def login_if_needed():
    global connected
    global ping_time

    if not connected or ping_time > MAX_CONNECTION_TIME:
        login()

def main():
    global connected
    local_path = None
    remote_path = None

    login()  # login pour initier la connexion

    print_banner()
    print_status()

    while True:
        print("")
        user_input = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
        print("")

        if user_input == "exit":
            break

        if user_input == "help":
            print_help()
            continue

        if user_input not in ["get", "send", "del", "ls", "mkdir", "status", "shell", "exit", "get-all", "send-all"]:
            print(f"{Fore.YELLOW}Invalid command. Use {Fore.GREEN}help{Fore.YELLOW} for help{Style.RESET_ALL}")
            continue

        if user_input == "shell":
            start_ssh_shell()
        elif user_input != "status" and user_input != "exit":
            remote_path = input("Server path --> ").strip()
            if user_input in ["get", "get-all", "send", "send-all"]:
                local_path = input(f"Local path {'' if user_input.startswith('get') else ''} --> ").strip()
                print("")
                if user_input.startswith("get") and not local_path:
                    print(f"{Fore.YELLOW}You need to specify a local path to use {Fore.GREEN}{user_input}{Style.RESET_ALL}")
                    continue
                if user_input.startswith("get"):
                    local_path = complete_local_path(local_path, default_local_path)

        if user_input != "status" and user_input != "exit":
            if user_input == "get-all":
                if not os.path.exists(local_path):
                    os.makedirs(local_path)
                remote_path = remote_path.rstrip('/')  # Remove trailing slash if present
                ssh_transfer("get-all", local_path, remote_path)
            elif user_input == "send-all":
                ssh_transfer("send-all", local_path, remote_path)
            else:
                ssh_transfer(user_input, local_path, remote_path)
            print("")
            print(f"{Fore.GREEN}{user_input}{Style.RESET_ALL} finished.\n")
        else:
            ssh_transfer(user_input, None, None)
            print_status()

        login_if_needed()  # refresh la connection

if __name__ == "__main__":
    main()
