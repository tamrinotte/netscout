# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from modules.logging_config import debug, info, error
from socket import (
    socket,
    AF_INET,
    SOCK_RAW,
    IPPROTO_ICMP,
    timeout as sockettimeout,
)
from struct import unpack
from time import time

##############################

# ICMP LISTENER

##############################

def icmp_listener(target_ip, closed_ports, stop_event, new_response_event, closed_ports_lock):
    try:
        sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
        sock.settimeout(1)
        debug("ICMP listener socket created.")
    except PermissionError:
        error("[!] ICMP listener requires root privileges.")
        stop_event.set()
        return
    except Exception as e:
        error(f"[!] Failed to create ICMP listener socket: {e}")
        stop_event.set()
        return

    info("ICMP listener started.")

    while not stop_event.is_set():
        try:
            packet, addr = sock.recvfrom(1024)
            if not packet:
                continue

            # Parse ICMP header
            icmp_header = packet[20:28]
            icmp_type, icmp_code, _, _, _ = unpack('bbHHh', icmp_header)

            if icmp_type == 3 and icmp_code == 3:
                ip_header_len = (packet[28] & 0x0F) * 4
                udp_header_offset = 28 + ip_header_len
                udp_header = packet[udp_header_offset:udp_header_offset + 8]

                if len(udp_header) < 8:
                    continue

                src_port, dst_port, _, _ = unpack('!HHHH', udp_header)

                if addr[0] == target_ip:
                    with closed_ports_lock:
                        closed_ports.add(dst_port)
                    new_response_event.set()  # Notify main thread
                    debug(f"ICMP Port Unreachable received for port {dst_port}")

        except sockettimeout:
            continue
        except Exception as e:
            error(f"Error while processing ICMP packet: {e}")
            continue

    sock.close()
    info("ICMP listener stopped.")