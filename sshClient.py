#!/usr/bin/env python3.6

# importlib.util to point directly to nocut: 
# https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
# https://stackoverflow.com/questions/1186789/what-is-the-best-way-to-call-a-python-script-from-another-python-script

import time

import paramiko
import getpass
from nocut3 import *
from netmiko import ConnectHandler

def sshClient(hostname = "115-2f-sw1", port=22):
    sshClient = paramiko.SSHClient()    # Create SSHClient instance
    # Below is policy that will automatically add missing host keys
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.load_system_host_keys()

    while True:
        username = input("username>>> ")
        password = getpass.getpass("password>>> ")
        cisco_device = {"device_type": "cisco_ios",
                        "ip": hostname,
                        "username": username,
                        "password": password,
                        "secret": secret}
        try:
            print("Connecting to device...")
            net_device = ConnectHandler(**cisco_device)
            net_device.enable()
            break
        except:
            print("Invalid credentials")
            continue

    while True:
        command = input(hostname + "#")
        if command.lower() == "exit":
            save_changes = input("Save any config changes? (y/n)>>> ")
            if save_changes.lower() == "y":
                output = net_device.send_command("copy run start")
                print(output)
                returnToNocut(net_device, save_changes=True)
                break
            else:
                returnToNocut(net_device, save_changes=False)
                break
        elif command.lower().startswith("con"):
            output = net_device.send_config_set(command,
                                                exit_config_mode=False)
            print(output)
            while True:
                command = input(hostname + "(config)#")
                if command.lower() == "exit":
                    net_device.exit_config_mode()
                    break
                elif command.lower().startswith("int"):
                    output = net_device.send_config_set(command,
                                                        exit_config_mode=False)
                    print(output)
                    while True:
                        command = input(hostname + "(config-if)#")
                        if command.lower() == "exit":
                            net_device.exit_config_mode()
                            break
                        else:
                            output = net_device.send_config_set(command,
                                                                exit_config_mode=False)
                            print(output)
                else:
                    output = net_device.send_config_set(command)
                    print(output)
        else:
            output = net_device.send_command(command)
            print(output)
            continue

def returnToNocut(device, save_changes=False):
    if save_changes:
        message = "[Config changes saved]"
    else:
        message = "[Config changes NOT saved]"
    print("%s Returning to nocut..." % (message))
    # close ssh connection first
    device.disconnect()
    time.sleep(3)
    mainFunction()

# if sshClient.py is called directly, sshClient()
if __name__ == "__main__":
    sshClient()