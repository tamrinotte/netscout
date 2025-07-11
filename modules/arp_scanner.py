# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from logging import debug, info, error
from modules.privileges import check_root_privileges
from ipaddress import ip_network, AddressValueError, NetmaskValueError
from sys import exit as sysexit
from scapy.all import ARP, Ether, srp
from time import time

##############################

# ARP SCANNER

##############################

def run_arp_scan(target_address, timeout=4):
    check_root_privileges()
    start_time = time()
    try:
        network = ip_network(target_address, strict=False)
        debug(f"Parsed target network: {network}")
        if network.version != 4:
            print("[!] ARP scan only supports IPv4 addresses.")
            sysexit(1)
    except (AddressValueError, NetmaskValueError) as e:
        print(f"[!] Invalid CIDR notation: {e}")
        sysexit(1)

    info(f"Starting ARP scan on network {network}")
    print("=== ARP Scan ===")
    print(f"[*] Performing ARP scan on {network}...")

    arp = ARP(pdst=str(network))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    try:
        ans, _ = srp(packet, timeout=timeout, verbose=0)
    except Exception as e:
        error(f"Failed to send ARP requests: {e}")
        return

    if not ans:
        print("[*] No hosts found.")
        return

    for _, received in ans:
        msg = f"IP Address: {received.psrc} - MAC Address: {received.hwsrc}"
        print(msg)

    end_time = time()
    duration = end_time - start_time
    print(f"\nDuration: {duration:.2f} seconds")
    info(f"ARP scan has been completed. Duration: {duration:.2f} seconds.")