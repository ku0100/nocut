#! /usr/bin/env python3.6

from sshClient import *

filepath = "/usr/local/telecom/wp/"
pinnaclefile = "/net/tms/pinnacle/downloads/prod/current/"

def pinnacle_get_switchport(jackID):
    jackID = jackID.upper()
    pinnacle_ports_file = pinnaclefile + "Export_Ports"
    # Open Pinncale_Ports file read-only
    pinnacle_ports = open(pinnacle_ports_file, "r")
    for i in pinnacle_ports:
        if jackID in i:
            # Found matching line with Jack ID, save the switch name, module number, and interface number
            ports = i.split()
            module = ports[0][-1] # equal 1
            switch = ports[0][:-2] # 003-1f-sw1
            pinnacle_ports.close()
            print("Switch     : %s\nInterface  : %s/%s" % (switch, module, ports[1],)) # 003-1f-sw1 1/14)
            device_login = input("Login to device? (y/n) >>> ")
            if device_login.lower() == "y":
                sshClient(hostname=switch)
    pinnacle_ports.close()
    print("Jack ID not active")

def pinnacle_get_IP(jackID):
    jackID = jackID.upper()
    pinnacle_IP_file = pinnaclefile + "Export_IP_Assignments"
    # Open Export_IP_Assignments file read-only
    pinnacle_IPs = open(pinnacle_IP_file, "r")
    # Create a list to add the IP addresses found to, since there may be >1
    ipAddresses = []
    for i in pinnacle_IPs:
        if jackID in i:
            line = i.split(',')
            # Found matching line with Jack ID, return the IP address
            ipAddresses.append(line[0])
    # Close the file
    pinnacle_IPs.close()
    
    # Check if we found any IPs and return them, or a message saying none were found
    if not ipAddresses:
        return "Jack doesn't have an IP address provisioned"
    else:
        return print_ips(ipAddresses)

def print_ips(ipList):
    for eachIP in ipList:
        print("IP: %s" % (str(ipList)))

def find_vlan_id (vlan_name):
    net_file = filepath + "networks"
    wp_net = open(net_file,"r")
    for x in wp_net:
        if x.startswith(vlan_name):
            vlans = x.split()
            wp_net.close()              # close networks.txt 
            return vlans[3]            # return vlan id 
