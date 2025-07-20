# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from socket import socket, AF_INET, SOCK_DGRAM, timeout as sockettimeout
from ipaddress import ip_address
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event, Lock, Thread
from time import time
from modules.logging_config import debug, info, error
from modules.privileges import check_root_privileges
from modules.icmp_listener import icmp_listener
from modules.service_recon import lookup_service_name

##############################

# UDP SCAN PORT

##############################

def run_udp_scan_port(target_ip, port, timeout=3, probe_payload=b''):
    protocol_name = 'udp'
    is_open = False
    response = ''
    try:
        with socket(AF_INET, SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            # Send probe payload or empty datagram
            sock.sendto(probe_payload if probe_payload else b'', (str(ip_address(target_ip)), port))
            try:
                data, _ = sock.recvfrom(4096)
                response = data.decode(errors='ignore').strip()
                is_open = True
                return {
                    'port': port,
                    'protocol_name': protocol_name,
                    'is_open': is_open,
                    'response': response,
                }
            except sockettimeout:
                return {
                    'port': port,
                    'protocol_name': protocol_name,
                    'is_open': is_open,
                    'response': '',
                }
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
    closed_ports_lock = Lock()
    stop_event = Event()
    new_response_event = Event()

    # ICMP listener thread
    listener_thread = Thread(
        target=icmp_listener,
        args=(target_ip, closed_ports, stop_event, new_response_event, closed_ports_lock)
    )
    listener_thread.daemon = True
    listener_thread.start()

    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(run_udp_scan_port, target_ip, port, timeout): port for port in ports}
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    debug(f"All UDP probes sent. Waiting for ICMP responses...")

    # Wait for ICMP quiet period or max_wait timeout
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

    # Categorize ports
    open_ports = []
    closed_ports_list = []
    open_filtered_ports = []

    for result in results:
        port = result['port']
        with closed_ports_lock:
            is_closed = port in closed_ports

        if is_closed:
            closed_ports_list.append(port)
        elif result['is_open']:
            open_ports.append(result)
        else:
            open_filtered_ports.append(port)

    # Output results
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

    # if closed_ports_list:
    #     debug("UDP ports closed (received ICMP Port Unreachable):")
    #     for p in closed_ports_list:
    #         debug(f"Port: {p}")
    #     print()

    if open_filtered_ports:
        print("UDP ports open|filtered (no response):")
        for p in open_filtered_ports:
            service_name = lookup_service_name(p, 'udp')
            print(f"Port: {p}")
            print(f"Service: {service_name}")
            print(f"Protocol: udp")
            print("State: Open|Filtered\n")

    duration = time() - start_time
    print(f"Duration: {duration:.2f} seconds")
    info(f"UDP scan completed in {duration:.2f} seconds.")