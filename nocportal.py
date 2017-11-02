#!/usr/bin/env python3.6

from nocut3 import *
from sshClient import *
from pinnacle import *

def portalMenu():
    print("NOC Portal (type 'exit' to exit:")
    print("1. nocut")
    print("2. jack lookup")
    print("3. dns")
    while True:
        selection = input("Please make a selection>>> ")
        if selection.lower() == "exit":
            sys.exit("Exiting the program!")
            break
        try:
            int(selection)
        except:
            print("Invalid selection")
            continue
        if int(selection) == 1:
            mainFunction()
            break
        elif int(selection) == 2:
            jackID = input("Jack ID >>> ")
            pinnacle_get_switchport(jackID)
            break
        elif int(selection) == 3:
            infobloxAuto()
            break
        else:
            print("Invalid selection")
            continue

if __name__ == "__main__":
    portalMenu()