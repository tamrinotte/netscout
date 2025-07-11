# NetScout
![NetScout](https://raw.githubusercontent.com/tamrinotte/netscout/python/app_images/netscout_logo.png)

NetScout is a port scanning tool that checks ports on a specified IP address or range. It supports scanning single ports or port ranges, identifies open ports, and attempts to determine the associated service name. The tool runs scans concurrently for speed and provides a summary of open ports along with scan duration.

<br>

## Installation

1) Download the installer.

	- Kali

	      curl -L https://github.com/tamrinotte/netscout/releases/download/python_kali_v0.1.0/netscout.deb -o netscout.deb

	- Debian

	      curl -L https://github.com/tamrinotte/netscout/releases/download/python_debian_v0.1.0/netscout.deb -o netscout.deb

2) Start the installer.

       sudo dpkg -i netscout.deb

<br>

## Options

__-h, --help:__ Displays the help message.

__ip_address:__ Target IP address (e.g., 10.10.10.10 or 192.168.1.0/24).

__--port PORT:__ Port number (e.g., 1005).

__--port-range PORT:__ Port range (e.g., 0-4000).

__--st:__ Scan for open TCP ports on the target.

__--su:__ Scan for open UDP ports on the target.

__--sa:__ Perform an ARP scan to discover hosts on the local network.

<br>

## Examples

1)
       netscout 10.10.10.10 -st

2)
       netscout 10.10.10.10 -st --port 3306

3)
       netscout 10.10.10.10 -st --port-range 0-4000

4)
       netscout 10.10.10.10/24 -sa

5)
       netscout 10.10.10.10 -su --port-range 0-4000

---

# NetScout
![NetScout](https://raw.githubusercontent.com/tamrinotte/netscout/python/app_images/netscout_logo.png)

NetScout, belirli bir IP adresi veya aralığındaki bağlantı noktalarını kontrol eden bir bağlantı noktası tarama aracıdır. Tek bağlantı noktalarının veya bağlantı noktası aralıklarının taranmasını destekler, açık bağlantı noktalarını tanımlar ve ilişkili hizmet adını belirlemeye çalışır. Araç, hız için taramaları eşzamanlı olarak çalıştırır ve tarama süresiyle birlikte açık bağlantı noktalarının bir özetini sağlar.

<br>

## Kurulum

1) Yükleyiciyi indirin.

	- Kali

	      curl -L https://github.com/tamrinotte/netscout/releases/download/python_kali_v0.1.0/netscout.deb -o netscout.deb

	- Debian

	      curl -L https://github.com/tamrinotte/netscout/releases/download/python_debian_v0.1.0/netscout.deb -o netscout.deb

2) Yükleyiciyi başlatın.

       sudo dpkg -i netscout.deb

<br>

## Seçenekler

__-h, --help:__ Yardım mesajını görüntüler.

__ip_address:__ Hedef IP adresi (ör. 10.10.10.10 veya 192.168.1.0/24).

__--port PORT:__ Bağlantı noktası numarası (ör. 1005).

__--port-range PORT:__ Bağlantı noktası aralığı (ör. 0-4000).

__--st:__ Hedefteki açık TCP bağlantı noktalarını tarayın.

__--su:__ Hedefteki açık UDP bağlantı noktalarını tarayın.

__--sa:__ Yerel ağdaki ana bilgisayarları keşfetmek için bir ARP taraması gerçekleştirin.

<br>

## Örnekler

1)
       netscout 10.10.10.10 -st

2)
       netscout 10.10.10.10 -st --port 3306

3)
       netscout 10.10.10.10 -st --port-range 0-4000

4)
       netscout 10.10.10.10/24 -sa

5)
       netscout 10.10.10.10 -su --port-range 0-4000

