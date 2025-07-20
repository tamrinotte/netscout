# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from socket import (
    socket,
    AF_INET,
    SOCK_STREAM,
    error as socket_error,
)
from ipaddress import ip_address
from concurrent.futures import ThreadPoolExecutor
from time import time
from modules.logging_config import debug, info, error
from modules.service_recon import grab_service_banner, lookup_service_name

##############################

# TCP SCAN PORT

##############################

def run_tcp_scan_port(target_ip, port, timeout=2):
    protocol_name = 'tcp'
    is_open = False
    banner = ''
    service_name = 'unknown'

    try:
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((str(ip_address(target_ip)), port))
            if result == 0:
                is_open = True
                service_name = lookup_service_name(port, protocol_name)
                # Pass port so banner grabber sends HTTP GET on 80 etc.
                banner = grab_service_banner(sock, timeout, port=port, protocol="tcp")

    except socket_error as se:
        error(f"Socket error on port {port}: {se}")
        return None
    except Exception as e:
        error(f"Unexpected error scanning port {port}: {e}")
        return None

    findings_dictionary = {
        'port': port,
        'service_name': service_name if is_open else 'unknown',
        'protocol_name': protocol_name,
        'is_open': is_open,
        'banner': banner
    }

    return findings_dictionary

##############################

# TCP SCAN

##############################

def run_tcp_scan(target_ip, ports, max_threads=100, timeout=2):
    start_time = time()
    print("=== TCP Scan ===")
    debug(f"Target IP Address = {target_ip}")
    debug(f"Target Port(s) = {ports}")

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(
            lambda port: run_tcp_scan_port(target_ip, port, timeout),
            ports
        )

    for result in results:
        if result is None or not result['is_open']:
            continue
        print(f"Port: {result['port']}")
        print(f"Protocol: {result['protocol_name']}")
        print(f"Service: {result['service_name']}")
        if result['banner']:
            print(f"Banner: ({result['banner']})")
        print(f"State: {'Open' if result['is_open'] else 'Closed'}\n")

    end_time = time()
    duration = end_time - start_time
    print(f"Duration: {duration:.2f} seconds")
    info(f"TCP scan has been completed. Duration: {duration:.2f} seconds.")
