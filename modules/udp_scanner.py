# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from socket import (
    socket,
    AF_INET,
    SOCK_DGRAM,
    timeout as sockettimeout,
)
from ipaddress import ip_address
from threading import Event, Thread
from concurrent.futures import ThreadPoolExecutor
from time import time, sleep
from modules.logging_config import debug, info, error
from modules.privileges import check_root_privileges
from modules.icmp_listener import icmp_listener
from modules.service_recon import lookup_service_name

##############################

# UDP SCAN PORT

##############################

def run_udp_scan_port(target_ip, port, timeout=3):
    protocol_name = 'udp'
    is_open = False
    response = ''
    try:
        with socket(AF_INET, SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.sendto(b'', (str(ip_address(target_ip)), port))
            try:
                data, _ = sock.recvfrom(1024)
                response = data.decode(errors='ignore').strip()
                is_open = True
                findings_dictionary = {
                    'port': port,
                    'protocol_name': protocol_name,
                    'is_open': is_open,
                    'response': response,
                }
                return findings_dictionary
            except sockettimeout:
                findings_dictionary = {
                    'port': port,
                    'protocol_name': protocol_name,
                    'is_open': is_open,
                    'response': '',
                }
                return findings_dictionary
    except Exception as e:
        error(f"UDP scan error on port {port}: {e}")
        return None

##############################

# UDP SCAN

##############################

def run_udp_scan(target_ip, ports, max_threads=100, timeout=3, quiet_timeout=2, max_wait=10):
    check_root_privileges()
    start_time = time()
    print("=== UDP Scan ===")

    closed_ports = set()
    stop_event = Event()
    new_response_event = Event()

    listener_thread = Thread(target=icmp_listener, args=(target_ip, closed_ports, stop_event, new_response_event))
    listener_thread.start()

    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(run_udp_scan_port, target_ip, port, timeout) for port in ports]
        for future in futures:
            res = future.result()
            if res:
                results.append(res)

    debug(f"All UDP probes sent. Waiting for ICMP responses...")

    icmp_wait_start = time()
    last_response_time = time()

    while (time() - icmp_wait_start) < max_wait:
        if new_response_event.wait(timeout=quiet_timeout):
            new_response_event.clear()
            last_response_time = time()
        elif (time() - last_response_time) >= quiet_timeout:
            debug(f"No ICMP replies in {quiet_timeout} seconds — assuming quiescence.")
            break

    stop_event.set()
    listener_thread.join()

    open_ports = []
    closed_ports_list = []
    open_filtered_ports = []

    for result in results:
        port = result['port']
        if port in closed_ports:
            closed_ports_list.append(port)
        elif result['is_open']:
            open_ports.append(result)
        else:
            open_filtered_ports.append(port)

    if open_ports:
        print("Open UDP ports (received UDP reply):")
        for result in open_ports:
            port = result['port']
            service_name = lookup_service_name(port, 'udp')
            print(f"Port: {port}")
            print(f"Service: {service_name}")
            print(f"Protocol: {result['protocol_name']}")
            if result['response']:
                print(f"UDP reply: {result['response']}")
            print("State: Open\n")

    if closed_ports_list:
        debug("UDP ports closed (received ICMP Port Unreachable):")
        for p in closed_ports_list:
            debug(f"Port: {p}")
        print()

    if open_filtered_ports:
        print("UDP ports open|filtered (no response):")
        for p in open_filtered_ports:
            service_name = lookup_service_name(p, 'udp')
            print(f"Port: {p}")
            print(f"Service: {service_name}")
            print(f"Protocol: {result['protocol_name']}")
            print("State: Open\n")

    duration = time() - start_time
    print(f"Duration: {duration:.2f} seconds")
    info(f"UDP scan completed in {duration:.2f} seconds.")
