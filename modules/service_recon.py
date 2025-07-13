# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from socket import getservbyport, error as socket_error
from logging import debug, info, error
from threading import Lock
from csv import DictReader
from json import load as jsonload

##############################

# GLOBAL VARIABLES

##############################

_services = {}
_services_loaded = False
_services_lock = Lock()
_probes = None

##############################

# LOAD IANA SERVICE-NAMES CSV FILE

##############################

def load_iana_services(path="data/service-names-port-numbers.csv"):
    global _services, _services_loaded
    with _services_lock:
        if _services_loaded:
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                reader = DictReader(file)
                for row in reader:
                    service_name = row["Service Name"].strip()
                    port = row["Port Number"].strip()
                    protocol = row["Transport Protocol"].strip().lower()

                    if not service_name or not port or not protocol:
                        continue

                    try:
                        port_number = int(port)
                        _services[(port_number, protocol)] = service_name
                    except ValueError:
                        continue

            _services_loaded = True
            debug(f"Loaded services from {path}")

        except Exception as e:
            error(f"Failed to load IANA services: {e}")

##############################

# SERVICE NAME LOOKUP

##############################

def lookup_service_name(port, protocol="tcp"):
    protocol = protocol.lower()

    # 1. Try system-level getservbyport
    try:
        service = getservbyport(port, protocol)
        debug(f"Resolved service via getservbyport: {service} on port {port}/{protocol}")
        return service
    except OSError:
        pass

    # 2. Try loaded IANA service names
    load_iana_services()
    service = _services.get((port, protocol), "unknown")
    debug(f"Resolved service via IANA services: {service} on port {port}/{protocol}")
    return service

##############################

# LOAD SERVICE PROBES

##############################

def load_probes(path="data/service-probes.json"):
    global _probes
    if _probes is not None:
        return _probes
    with open(path, "r", encoding="utf-8") as f:
        _probes = jsonload(f)
    # Decode escape sequences in payloads
    for probe in _probes:
        probe["probe_payload"] = probe["probe_payload"].encode("utf-8").decode("unicode_escape")
        debug(probe)
    return _probes

##############################

# FIND SERVICE PROBES

##############################

def find_probe(port, protocol):
    probes = load_probes()
    protocol = protocol.lower()
    for probe in probes:
        if probe["port"] == port and probe["protocol"] == protocol:
            return probe
    return None

##############################

# BANNER GRABBER

##############################

def grab_service_banner(sock, timeout=2, port=None, protocol="tcp"):
    banner = ""
    try:
        sock.settimeout(timeout)
        probe = None

        # For HTTP(S) ports, send explicit GET request to get headers only
        if port in (80, 443) and protocol.lower() == "tcp":
            probe = "GET / HTTP/1.0\r\n\r\n"
            debug(f"Sending HTTP GET probe for port {port}")

        else:
            if port is not None:
                probe_data = find_probe(port, protocol)
                if probe_data:
                    probe = probe_data["probe_payload"]
                    debug(f"Sending probe payload for {protocol.upper()} port {port}: {probe.strip()}")

        if probe:
            sock.sendall(probe.encode())

        data_chunks = []
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                data_chunks.append(data)
            except Exception:
                break

        if data_chunks:
            full_banner = b"".join(data_chunks).decode(errors='ignore').strip()
            debug(f"Received full banner:\n{full_banner}")

            # For HTTP, extract headers (everything before first double CRLF)
            if port in (80, 443) and protocol.lower() == "tcp":
                header_end = full_banner.find("\r\n\r\n")
                if header_end != -1:
                    banner = full_banner[:header_end].strip()
                else:
                    banner = full_banner  # fallback: entire banner if no header boundary found
            else:
                banner = full_banner

        info("Banner grabbing completed.")

    except Exception as e:
        error(f"Failed to grab banner: {e}")

    return banner