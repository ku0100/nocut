#! /usr/bin/env python3.6

import os
import re
import time
import sys

import ipaddress # This is for IP address validation
from netaddr import *
from ipinfo import *

mac_data_dir = "/net/mactables/data/"
dupe = "/net/arpcache/bin/DupeChecker/"
filepath = "/usr/local/telecom/wp"


# Check whether the building number exists in the MAC table directory
# Returns True/False
def validBldg(bldg_num):
    bldg_dir = os.path.join(mac_data_dir, bldg_num)
    return os.path.exists(bldg_dir)

# MAC address search
def macSearch(bldg_num, mac_addr, last_seen):
    if (bldg_num):
        bldg_dir = os.path.join(mac_data_dir, bldg_num)
    else:
        bldg_dir = mac_data_dir # if bldg not found, search all bldgs
    found_switch = []
    last_seen = last_seen.split("-")
    last_seen = last_seen[0].split("/")
    last_seen = last_seen[2] + last_seen[0]
    
    try:
        if (os.path.isdir(bldg_dir)):
            # Check only "YYYYMMDDhhmm" file format
            filename_pattern = re.compile(last_seen)
            # Exception handling
            for file in reversed(os.listdir(bldg_dir)):
                path = bldg_dir + "/" + file
                if ((time.time() - os.path.getctime(path))
                    < (30 * 24 * 60 * 60)) and re.match(filename_pattern,
                                                        file):
                    f = open(path, "r")
                    for line in f.readlines():
                        if (mac_addr in line and line not in found_switch):
                            found_switch.append(file)
                            found_switch.append(line)
                            # break
                            return found_switch
                        f.close()
                    else:
                        pass
                return found_switch
    except:
        return 0

def bldgNumInput():
    i = 0
    while (i < 2):
        bldg_input = input("\n> Building num: ")
        # Remove white spaces
        bldg_input = bldg_input.replace(" ", "")
        # Remove leading 0's
        bldg_input = bldg_input.lstrip("0")
        if (bldg_input.lower() == "exit"):
            sys.exit("Exiting the program!")
        elif (bldg_input == ""):
            i += 1
            continue
        elif (validBldg(bldg_input)):
            return bldg_input
        else:
            print("Not a valid building number")
            i += 1
            continue

def macStringCoversion(mac_input):
    # Format mac to EUI
    mac = EUI(mac_input)
    # Specify cisco mac formatting (0123.45AB.CDEF)
    mac.dialect = mac_cisco
    mac_addr = str(mac)
    return mac_addr

def searchMacTable(command):
    output = os.popen(command).read()
    # Multiple output handling
    lines = output.split("\n")
    lines = [line for line in lines if line != ""] # can this just say [line in lines if line != ""]??
    
    # Single dupe handling
    if (len(lines) == 3):
        displaySwitchInfo(lines[2], command)
    # Multiple dupe handling
    elif (len(lines) > 3):
        selectDupe(lines)
    else:
        print("\n No connected switch information found")

def displaySwitchInfo(line, command=0):
    line = line.split()
    ip_addr = line[0]
    mac_addr = macStringConversion(line[1])
    first_seen = line[2]
    last_seen = line[3]

    # Netaddr reference (IPNetwork)
    ip_addr = IPNetwork(ip_addr)
    # ipinfo.py reference (IpFinder)
    uip = IpFinder(ip_addr)
    if (command is 0):
        pass
    elif ("-m" in command):
        uip.printOutput()
    print("MAC          : %s" % (mac_addr))

    bldg = BldgFinder(uip.vlan_name, uip.vlan_id)
    # ipinfo.py reference (locateBldgNumber)
    bldg_guess = bldg.locateBldgNumber()
    if (bldg_guess == "0"):
        print(" Backbone Network device")
    else:
        switch_info = macSearch(bldg_guess, mac_addr, last_seen)
        j = 0
        while (j < 2):
            if (switch_info):
                switch = switch_info[1].split("\t")
                print("\n------------------------------------------------")
                print(" History      : %s \t %s" % (switch[0], switch[2]))
                print(" Date         : %s " % (switch_info[0]))
                protocol = "~kuwillia/Python/ssh2.pl "
                switch_connect = (protocol + switch[0] + " " + mac_addr)
                print("------------------------------------------------")
                print(" Searching    : %s" % (switch[0]))
                output = os.popen(switch_connect).read()
                print(output)
                print("------------------------------------------------")
                break
            else:
                print("\n Cannot find in building %s" % (bldg_guess))
                i += 1
                bldg_guess = bldgNumInput()
                if (bldg_guess > 0):
                    switch_info = macSearch(bldg_guess, mac_addr, last_seen)

def dupeSelector(lines):
    k = 0
    print
    print(" -------------------------------- Dupe Result --------------------------------")
    print("          IP             |         MAC     |     First Seen     |    Last Seen ")
    for line in lines[2:]:
        l = line.split()
        if (len(l) == 4):
            k += 1
            print("%s) %s      %s    %s    %s" % (k, l[0], l[1], l[2], l[3]))
    print(" ------------------------------------------------------------------------------")

    while True:
        number = input("\n Select number for detailed switch info >> ")
        if (number.lower() == "exit"):
            sys.exit("Exiting the program!")
        elif (number == ""):
            pass
        try:
            int(number)
            if (0 < int(number) <= k):
                displaySwitchInfo(lines[int(number) + 1], "-m")
            else:
                print(" Not a valid choice ")
                pass
        except:
            print(" Not a valid choice ")
            continue



if len(sys.argv) > 1:
	user_input = str(sys.argv[1])

	# Input mac or ip
	user_input = user_input.replace(" ","")  #remove all space

	if user_input.lower() == "exit":
			sys.exit( " Thank you for using NoCut - HJ ")
			sys.exit()

	elif valid_ipv4(user_input):
			ip_addr = user_input
			dip = IpFounder(IPNetwork(user_input))

			if dip.is_umd_ip:
					dip.print_output()
					command = dupe+' -i '+ip_addr
					search_mac_table(command)
			else : print ip_addr ,"is not valid UMD IP"
			sys.exit()

	elif valid_mac(user_input):
			mac_addr = mac_to_string(user_input)
			command = dupe+' -m '+mac_addr
			search_mac_table(command)

	else:
			print  user_input, "neither IP or MAC. please try again"
			sys.exit()


else:

	os.system('clear')
	print ('#-------------------------------------------------------#')
	print ('#  Hi. HJ\'s NoCut! tracking switch port with mac or IP')
	print ('#  Input any form of MAC or IP address - ddomu@umd.edu  ')
	print ('#-------------------------------------------------------#\n')

	while True:

		# Input mac or ip
		user_input = raw_input('\n ip address or mac address or exit to quit:')
		user_input = user_input.replace(" ","")  #remove all space

		if user_input.lower() == "exit":
				sys.exit( " Thank you for using NoCut - HJ ")
				break
		elif user_input == "":
				continue
		elif valid_ipv4(user_input):
				ip_addr = user_input
				dip = IpFounder(IPNetwork(user_input))

				if dip.is_umd_ip:
						dip.print_output()
						command = dupe+' -i '+ip_addr
						search_mac_table(command)
				else : print '\n ', ip_addr ,"is not valid UMD IP"

		elif valid_mac(user_input):
				mac_addr = mac_to_string(user_input)
				command = dupe+' -m '+mac_addr
				search_mac_table(command)

		else:
				print  user_input, "neither IP or MAC. please try again"
				continue

