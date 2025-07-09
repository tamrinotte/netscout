# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from socket import (
    socket,
    AF_INET,
    SOCK_STREAM,
    getservbyport,
    error as socket_error,
)
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
from sys import exit as sysexit
from ipaddress import ip_address
from logging import (
    basicConfig,
    DEBUG,
    CRITICAL,
    disable,
    debug,
    info,
    error,
)
from time import time



##############################

# LOGGING CONFIG

##############################

basicConfig(level=DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
disable(CRITICAL)



##############################

# NetScout

##############################

class NetScout:
    def __init__(self, target_ip_address, target_port_specification):
        self.max_threads=100
        self.target_ip_address = target_ip_address
        self.target_port_specification = target_port_specification

    ##############################

    # SCAN

    ##############################

    def scan(self, port):
        service_name = 'unknown'
        protocol_name = 'tcp'
        state = False
        try:
            try:
                service_name = getservbyport(port)
            except OSError:
                error("Couldn't get the service's name.")
                pass  # just leave it as 'unknown'

            with socket(AF_INET, SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex((str(ip_address(self.target_ip_address)), port))
                if result == 0:
                    state = True
        except socket_error:
            error(f"Socket error on port {port}")
            return None
        except Exception as e:
            error(f"Unexpected error scanning port {port}: {e}")
            return None

        return {
            'port': port,
            'service_name': service_name if state else 'unknown',  # only meaningful if open
            'protocol_name': protocol_name,
            'open': state
        }

    ##############################

    # START

    ##############################

    def start(self):
        start_time = time()
        print("=== Findings ===")
        debug(f"Target IP Address = {self.target_ip_address}")
        debug(f"Target Port(s) = {self.target_port_specification}")
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            results = executor.map(self.scan, self.target_port_specification)
        for index, result in enumerate(results, start=1):
            if result is None or not result['open']:
                continue
            print(f"Port: {result['port']}")
            print(f"Protocol: {result['protocol_name']}")
            print(f"Service: {result['service_name']}")
            print(f"State: {'Open' if result['open'] else 'Closed'}")
            print()
        end_time = time()
        duration = end_time - start_time
        print(f"Duration: {duration:.2f} seconds")
        info(f"Port(s) has been scanned. It took {duration}")



##############################

# MAIN

##############################

def main():
    parser = ArgumentParser(description="Port Scanning Tool")
    parser.add_argument("ip_address", help="Target ip address (e.g., 10.10.10.10 or 10.10.10.10/24).")
    port_group = parser.add_mutually_exclusive_group(required=False)
    port_group.add_argument("--port", type=int, help="Target port (e.g., 22).")
    port_group.add_argument("--port-range", help="Target port range (e.g., 0-1000).")
    args = parser.parse_args()

    if args.port:
        target_port_specification = [args.port]
    elif args.port_range:
        try:
            start, end = map(int, args.port_range.split('-'))
            if start > end:
                parser.error("--port-range must be in the format 'start-end' where start is less than or equal to end")
                sysexit()
            target_port_specification = list(range(start, end + 1))
        except ValueError:
            parser.error("--port-range must be in the format 'start-end'")
    else:
        target_port_specification = list(range(0, 1001))

    netscout = NetScout(
        target_ip_address=args.ip_address,
        target_port_specification=target_port_specification,
    )
    netscout.start()

if __name__ == "__main__":
    main()