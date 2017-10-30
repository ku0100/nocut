#!/usr/bin/env python3.6

# importlib.util to point directly to nocut: 
# https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
# https://stackoverflow.com/questions/1186789/what-is-the-best-way-to-call-a-python-script-from-another-python-script

import importlib.util
import paramiko
import getpass

def sshClient(hostname, port=22):
    self.hostname = hostname
    self.port = port
    sshClient = paramiko.SSHClient()    # Create SSHClient instance
    # Below is policy that will automatically add missing host keys
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.load_system_host_keys()
    username = input("username>>> ")
    password = getpass.getpass(input("password>>> "))
    client.connect(hostname, port, username, password)
    while True:
        command = input(hostname + "#")
        try:
            if (command.lower() == "exit"):
                print("Returning to nocut...")
                nocut3.mainFunction()
            stdin, stdout, stderr = sshClient.exec_command(command)
            print(stdout.read())
            continue
        except:
            print("Invalid command!")
            continue
