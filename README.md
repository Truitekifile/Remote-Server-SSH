# Remote-Server-SSH

Remote server SSH, is a tool that aim to facilitate the use of a second computer as a server to manage files

# Installation

## You need to have PIP and python installed on your host computer and on the server (also it work on ubuntu but i never tested it on windows so idk)

Clone the repository with git :
```
git clone https://github.com/Truitekifile/Remote-Server-SSH/
```
Or download and extract the repository with 7zip


When the repository is ready, go into the RS-SSH folder and run :
```
pip install -r requirements.txt
```
This will install everything you need to run the tool

# Configuring RS-SSH

Once everything is installed, you first need to configure some things in the script before launching it.

Open remote_server_ssh.py with a text or code editor, such as notepad or Visual Studio Code, and go to __SSH_Informations__ :

Replace IP with the IP adress of the server you want to access :
```
SSH_HOST = 'IP'
```
Replace Username with the name of the user you are using on the server
```
SSH_USERNAME = 'Username' # hostname
```
You can also add a default path if you want to avoid typing the whole path each time
```
default_local_path = r'Your default path without the ("")'
```
If you want to automate the process of login in, you can add a file named __login__ with no extension in the script folder and writing your password inside of it. However i wouldn't recommend doing that for obvious security reasons. But if you feel like it, go ahead. Also, this will not be used to connect to a shell, you need to type the password manually

# Running RS-SSH

Now that the tool is installed and configured, here is two method to launch it:

### Using python and a terminal :

Go in the tool folder, open a terminal and type
```
python remote_server_ssh.py
```
But this is long and anoying to write this each time. So you can also just ...

### Using the .bat file :

Use the .bat file I already made to make your life easier. 

When the tool is launched, it should look like that:

![image](https://github.com/Truitekifile/Remote-Server-SSH/assets/91056971/a2932f24-61de-4f27-a51a-1b5c3f861f26)

__Available commands:__

  get <remote_path> [local_path]: Download a file or a folder from the server
  send <local_path> [remote_path]: Send a file or a folder to the server
  del <remote_path>: Delete a file or a folder on the server
  ls <remote_path>: List the contents of <remote_path> on the server
  mkdir <remote_path>: Create a folder on the server
  status: Check SSH connection to the server
  shell: Start a shell connected to the server
  get-all <remote_path> [local_path]: Download the entire contents of a folder from the server
  send-all <local_path> [remote_path]: Send the entire contents of a folder to the server
  help: Print help
  exit: Exit the tool

### You need to specify the name of the file on the two path (local and server)
Like this :

> /home/user/save/file.txt
> c:/users/user/downloads/file.txt

Otherwise your file will be rename like the last part of your path, in this case save/, lol
  





