#!/usr/bin/env python

import os
import re
import sys
import socket

from netaddr import *
pinnaclefile = "/net/tms/pinnacle/downloads/prod/current/"

def pinnacle_get_switchport(jackID):
    pinnacle_ports_file = pinnaclefile + "Export_Ports"
    # Open Pinncale_Ports file read-only
    pinnacle_ports = open(pinnacle_ports_file, "r")
    for i in pinnacle_ports:
        ports = i.split()
        if(ports[2].startswith(jackID)):
                pinnacle_ports.close()
                # Found matching line with Jack ID, save the switch name, module number, and interface number
                module = ports[0][-1] # equal 1
                switch = ports[0][:-2] # 003-1f-sw1
                return switch + " " + module + "/" + ports[1] # 003-1f-sw1 1/14

def pinnacle_get_jackID(switchport):
    pinnacleports = pinnaclefile + "Export_Ports"
    # Open Pinncale_Ports file read-only
    pinnacle_ports = open(pinnacleports, "r")
    for i in pinnacle_ports:
        ports = i.split()
        switchANDport = ports[0] + ports[1]
        if(switchANDport.startswith(switchport)):
                pinnacle_ports.close()
                # Return jackID from Export_Ports
                switchport = ports[2]
                return switchport

filepath = '/usr/local/telecom/wp/'

def vlanIDLocator(vlan_name):
    networks_file = filepath + "networks"
    # Open networks.txt read-only
    wp_networks = open(networks_file, "r")
    for i in wp_networks:
        if(i.startswith(vlan_name)):
            vlans = i.split()
            wp_networks.close()
            # Return VLAN column value from networks.txt
            return vlans[3]

class IpFinder:

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr
        wp_ips = filepath + "ipconfig"
        try:
            # Open ipconfig.txt read-only
            ip_text = open(wp_ips, "r")
            lines = wp_ips.readlines()
            self.umd_public_ip = False
            for line in lines:
                if (line.startswith("#") == False):
                    columns = line.split()
                    if (len(columns) > 4 and columns[2] == "range"):
                        # Netaddr reference (IPNetwork)
                        ip_network = IPNetwork(columns[4])
                        if (ip_addr in ip_network):
                            self.umd_public_ip = True
                            self.vlan_name = columns[0]
                            self.vlan_id = vlanIDLocator(self.vlan_name)
                            # Netaddr reference (.netmask)
                            self.subnet_mask = ip_network.netmask
                            self.gateway = ip_network[1]
                            break
            ip_text.close()
        except FileNotFoundError:
            print("Error: File not found", wp_ips)
            sys.exit(3)

    def printOutput(self):
        print(" IP Addr      : %s" % (self.ip_addr))
        print(" vLAN ID      : %s" % (self.vlan_id))
        print(" VLAN Name    : %s" % (self.vlan_name))
        print(" Subnet Mask  : %s" % (self.subnet_mask))
        print(" Gateway      : %s" % (self.gateway))

class BldgFinder:

    def __init__(self, vlan_name, vlan_number):
        self.vlan_name = vlan_name
        self.vlan_number = vlan_number

    def locateBldgNumber(self,):
        vlan_name = self.vlan_name
        bldg_pattern = re.compile("(\d{1,3})[a-z]")
        backbone_pattern = re.compile("0[a-z]")
        wifi_pattern = re.compile("100[0-9][a-z]")
        css_pattern = re.compile("1011[a-z]")
        ptx_pattern = re.compile("1010[a-z]")
        fw_pattern = re.compile("(\d{4})[a-z]")
        if (bldg_pattern.match(vlan_name)
            or backbone_pattern.match(vlan_name)):
            bldg_number = re.sub("\D", "", vlan_name)
            return bldg_number
        elif (wifi_pattern.match(vlan_name)):
            bldg_number = "wireless"
            return bldg_number
        elif css_pattern.match(vlan_name):
            bldg_number = "224"
            return bldg_number
        elif ptx_patter.match(vlan_name):
            bldg_number = "10"
            return bldg_number
        elif fw_pattern.match(vlan_name):
            bldg_number=re.sub("\D", "", vlan_name)
            # Remove first number b/c firewall
            bldg_number = bldg_number[1:]
            return bldg_number
        else:
            return False

# Python ipinfo.py
if (__name__ == "__main__"):
    os.system("clear")
    while True:
        valid_ip = input("\nEnter an IP address or type 'exit' to stop:\n> ")
        valid_ip = valid_ip.replace(" ", "")
        if (valid_ip == ""):
            continue
        elif (valid_ip.lower() == "exit"):
            sys.exit("Exiting the program!")
        # Netaddr reference (.valid_ipv4)
        elif (valid_ipv4(valid_ip)):
            ip_addr = IPNetwork(valid_ip)
            uip = IpFinder(ip_addr)
            if (uip.umd_public_ip == False):
                print("%s : Not a valid UMD IP, please enter again"
                    % (valid_ip))
                continue
            else:
                print(" IPV4 Address : %s" % (ip_addr.ip))
                print(" vLAN ID      : %s" % (uip.vlan_id))
                print(" VLAN Name    : %s" % (uip.vlan_name))
                print(" Subnet Mask  : %s" % (uip.subnet_mask))
                print(" Gateway      : %s" % (uip.gateway))
                bldg = BldgFinder(uip.vlan_name, uip.vlan_id)
                print(" Building     : %s" % (bldg.locateBldgNumber()))
                continue
        else:
            print("%s : Not a valid UMD IP, please enter again" % (valid_ip))
            continue

