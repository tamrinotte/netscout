# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from argparse import ArgumentParser
from sys import exit as sysexit
from modules.logging_config import(
    debug,
    info,
    error,
)
from modules.arp_scanner import run_arp_scan
from modules.tcp_scanner import run_tcp_scan
from modules.udp_scanner import run_udp_scan

##############################

# NetScout

##############################

class NetScout:
    def __init__(
        self,
        target_ip_address,
        target_port_specification,
        is_arp_scan_requested,
        is_tcp_scan_requested,
        is_udp_scan_requested
    ):
        self.max_threads = 100
        self.target_ip_address = target_ip_address
        self.target_port_specification = target_port_specification
        self.is_arp_scan_requested = is_arp_scan_requested
        self.is_tcp_scan_requested = is_tcp_scan_requested
        self.is_udp_scan_requested = is_udp_scan_requested

    ##############################

    # ARP SCAN

    ##############################

    def perform_arp_scan(self):
        run_arp_scan(target_address=self.target_ip_address)

    ##############################

    # TCP SCAN

    ##############################

    def perform_tcp_scan(self):
        run_tcp_scan(
            target_ip=self.target_ip_address,
            ports=self.target_port_specification,
            max_threads=self.max_threads
        )

    ##############################

    # UDP SCAN

    ##############################

    def perform_udp_scan(self, timeout=3):
        run_udp_scan(
            target_ip=self.target_ip_address,
            ports=self.target_port_specification,
            max_threads=self.max_threads
        )

    ##############################

    # START

    ##############################

    def start(self):
        if self.is_arp_scan_requested:
            self.perform_arp_scan()
        if self.is_tcp_scan_requested:
            self.perform_tcp_scan()
        if self.is_udp_scan_requested:
            self.perform_udp_scan()


##############################

# HELPER FUNCTIONS

##############################

def parse_port_specification(parser, args):
    if args.port:
        return [args.port]
    elif args.port_range:
        try:
            start, end = map(int, args.port_range.split('-'))
            if start > end:
                parser.error("--port-range must be in the format 'start-end' where start <= end")
                sysexit()
            return list(range(start, end + 1))
        except ValueError:
            parser.error("--port-range must be in the format 'start-end'")
    else:
        return list(range(0, 1001))

##############################

# MAIN

##############################

def main():
    parser = ArgumentParser(description="NetScout: Port & ARP Scanner")
    parser.add_argument("ip_address", help="Target IP address (e.g., 10.10.10.10 or 192.168.1.0/24).")
    port_group = parser.add_mutually_exclusive_group(required=False)
    port_group.add_argument("--port", type=int, help="Target port (e.g., 22).")
    port_group.add_argument("--port-range", help="Target port range (e.g., 0-1000).")
    scan_group = parser.add_mutually_exclusive_group(required=False)
    scan_group.add_argument('-st', action="store_true", help="Scan for open TCP ports on the target.")
    scan_group.add_argument('-sa', action="store_true", help="Perform an ARP scan to discover hosts on the local network.")
    scan_group.add_argument('-su', action="store_true", help="Scan for open UDP ports on the target.")
    args = parser.parse_args()
    target_port_specification = parse_port_specification(parser, args)
    netscout = NetScout(
        target_ip_address=args.ip_address,
        target_port_specification=target_port_specification,
        is_arp_scan_requested=args.sa,
        is_tcp_scan_requested=args.st,
        is_udp_scan_requested=args.su,
    )
    netscout.start()

if __name__ == "__main__":
    main()