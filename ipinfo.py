#!/usr/bin/env python
################################################
#	~ddomu/python/ipinfo.py
#	HJ Park (ddomu@umd.edu ) 
#----------------------------------------------
#	Input : IP address
#	Output : Vlan name, Vlan ID, Subnet Mask, Gateway 
#
################################################
from netaddr import *
import socket
import os,sys,re
filepath = '/usr/local/telecom/wp/'
pinnaclefile = "/net/tms/pinnacle/downloads/prod/current/"

def pinnacle_get_switchport(jackID):

	jackID = jackID.upper()
	pinnacle_ports_file = pinnaclefile + "Export_Ports"
	# Open Pinncale_Ports file read-only
	pinnacle_ports = open(pinnacle_ports_file, "r")
	for i in pinnacle_ports:
		if jackID in i:
			ports = i.split()
			pinnacle_ports.close()
			# Found matching line with Jack ID, save the switch name, module number, and interface number
			module = ports[0][-1] # equal 1
			switch = ports[0][:-2] # 003-1f-sw1
			return switch + " " + module + "/" + ports[1] # 003-1f-sw1 1/14

def find_vlan_id (vlan_name):

	net_file = filepath + 'networks'
	wp_net = open (net_file,'r')
	for x in wp_net:
		if x.startswith(vlan_name) :
			vlans = x.split()
			wp_net.close()				# close networks.txt 
			return vlans[3]				# return vlan id 
	
####################	IP address input 	####################
class IpFounder:

	def __init__(self,ip_addr):
		self.ip_addr = ip_addr 
		ip_file = filepath + 'ipconfig'
		try:
			ip_txt = open(ip_file, 'r') 
			lines = ip_txt.readlines()
			self.is_umd_ip = False			
			
			for line in lines:
				if not line.startswith("#"):				# ignore comment line 
					words = line.split()
					if(len(words) > 4 and words[2] == 'range'): 		# If the line has network range
						ip_network = IPNetwork(words[4]) 		 		# ip_network object create
						####################	Find IP address range  ####################
						if ip_addr in ip_network:			 # If ip_addr is included in ip_network range
							self.is_umd_ip = True
							self.vlan_name = words[0]			 # vlan_name 
							self.vlan_id = find_vlan_id(self.vlan_name)
							self.subnet_mask = ip_network.netmask
							self.gateway = ip_network[1] 
							break
									# ip_address, vlan name, vlan id, subnet mask, gateway 
			ip_txt.close()
		except FileNotFoundError:
			print "Error : fail to open", ip_file
			sys.exit(0)
	def print_output(self):
		print " IP addr      : ",self.ip_addr
		print " vlan_id      : ",self.vlan_id
		print " vlan_name    : ",self.vlan_name 		 
		print " subnet mask  : ",self.subnet_mask	 
		print " gateway      : ",self.gateway	 
	
			

class bldFounder:			
	def __init__(self, vlan_name, vlan_number):
		self.vlan_name = vlan_name
		self.vlan_number = vlan_number 

#		if not self.vlan_name: self_num=''			# Return Error 
#		else:
#			self.num = get_bld_number(vlan_name) 
	
	def get_bld_number(self,):
		vlan_name = self.vlan_name
		bld_pattern = re.compile ('(\d{1,3})[a-z]')
		backbone_pattern = re.compile ('0[a-z]')
		wifi_pattern = re.compile ('100[0-9][a-z]') 
		css_voip_pattern = re.compile ('1011[a-z]')
		ptx_pattern = re.compile ('1010[a-z]') 
		fw_pattern = re.compile ('(\d{4})[a-z]')
		
		# case 1 : building network \d{1,3}\w  e.g. 3a to 369z 		
		# case 2 : backbone network '0'\w
		if wifi_pattern.match(vlan_name) : 
			bld_number = 'wireless'
			return bld_number
		elif bld_pattern.match(vlan_name) or backbone_pattern.match(vlan_name): 
			bld_number = re.sub('\D',"",vlan_name)
			return bld_number
		# case 3 : wireless network '100'\d\w
		elif wifi_pattern.match(vlan_name) : 
			bld_number = 'wireless'
			return bld_number
		# case 4 : CSS VoIP network '101'\d\w
		elif css_voip_pattern.match(vlan_name) : 
			bld_number = '224'
			return bld_number
		elif ptx_pattern.match(vlan_name) : 
			bld_number = '10'
			return bld_number 
		# case 5 : \d{4}[a-z] 1115a ~ 5224e 
		elif fw_pattern.match(vlan_name) :
			bld_number = re.sub('\D',"",vlan_name)
			bld_number = bld_number[1:]			# remove first numeric 
			return bld_number 
		return False
			
	
####################	Main Function 	####################
if __name__ == '__main__' : 		# python ipinfo.py 
	os.system('clear')

	while 1:
		is_ip = raw_input('Enter an IP address or type "exit" to stop:')
		is_ip = is_ip.replace(" ","")  #remove all space

		if is_ip == "": 	continue
		elif is_ip.lower() == "exit":
			print ("Thank you for using ipinfo - HJ ")
			break					
		elif valid_ipv4(is_ip):				
			ip_addr = IPNetwork(is_ip)
			dip = IpFounder(ip_addr)
	
			if not dip.is_umd_ip:
				print is_ip, " : NOT a valid UMD IP address, please try again" 
				continue
			else :
				print "IPv4 address : ",ip_addr.ip
				print "vlan_id      : ",dip.vlan_id
				print "vlan_name    : ",dip.vlan_name 		 
				print "subnet mask  : ",dip.subnet_mask	 
				print "gateway      : ",dip.gateway	 
				bld = bldFounder(dip.vlan_name,dip.vlan_id)
				print "Building     : ",bld.get_bld_number()
				continue
		else: 
			print  is_ip, ": NOT a valid IP address, please try again"
			continue
	
