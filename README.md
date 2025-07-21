# NetScout
![NetScout](https://raw.githubusercontent.com/tamrinotte/netscout/python/app_images/netscout_logo.png)

NetScout is a port scanning tool that checks ports on a specified IP address or range. It supports scanning single ports or port ranges, identifies open ports, and attempts to determine the associated service name. The tool runs scans concurrently for speed and provides a summary of open ports along with scan duration.

<br>

## Installation

1) Install dependencies.

       sudo apt update
       sudo apt install libpcap-dev

2) Download the installer.

	- Kali

	      curl -L https://github.com/tamrinotte/netscout/releases/download/go_kali_v0.1.0/netscout.deb -o netscout.deb

	- Debian

	      curl -L https://github.com/tamrinotte/netscout/releases/download/go_debian_v0.1.0/netscout.deb -o netscout.deb

2) Start the installer.

       sudo dpkg -i netscout.deb

<br>

## Options

__-h:__ Displays the help message.

__-ip string:__ Target IP address (e.g., 10.10.10.10 or 192.168.1.0/24).

__-p int:__ Target port (e.g., -p=22).

__-pr string:__ Target port range (e.g., -pr=0-1000).

__-sa:__ Perform an ARP scan to discover hosts on the local network.

__-st:__ Scan for open TCP ports on the target.

__-su:__ Scan for open UDP ports on the target.

<br>

## Examples

1)
       netscout -ip=10.10.10.10 -st

2)
       netscout -ip=10.10.10.10/24 -sa

3)
       netscout -ip=10.10.10.10 -st -p=3306

4)
       netscout -ip=10.10.10.10 -st -pr=0-4000

5)
       netscout -ip=10.10.10.10 -su -p=9999

6)
       netscout -ip=10.10.10.10 -su -pr=0-4000

---

# NetScout
![NetScout](https://raw.githubusercontent.com/tamrinotte/netscout/python/app_images/netscout_logo.png)

NetScout, belirli bir IP adresi veya aralığındaki bağlantı noktalarını kontrol eden bir bağlantı noktası tarama aracıdır. Tek bağlantı noktalarının veya bağlantı noktası aralıklarının taranmasını destekler, açık bağlantı noktalarını tanımlar ve ilişkili hizmet adını belirlemeye çalışır. Araç, hız için taramaları eşzamanlı olarak çalıştırır ve tarama süresiyle birlikte açık bağlantı noktalarının bir özetini sağlar.

<br>

## Kurulum


1) Bağımlılıkları yükleyin.

       sudo apt update
       sudo apt install libpcap-dev

2) Yükleyiciyi indirin.

	- Kali

	      curl -L https://github.com/tamrinotte/netscout/releases/download/go_kali_v0.1.0/netscout.deb -o netscout.deb

	- Debian

	      curl -L https://github.com/tamrinotte/netscout/releases/download/go_debian_v0.1.0/netscout.deb -o netscout.deb

3) Yükleyiciyi başlatın.

       sudo dpkg -i netscout.deb

<br>

## Seçenekler

__-h:__ Yardım mesajını görüntüler.

__-ip string:__ Hedef IP adresi (ör. 10.10.10.10 veya 192.168.1.0/24).

__-p int:__ Hedef bağlantı noktası (ör. -p=22).

__-pr string:__ Hedef bağlantı noktası aralığı (ör. -pr=0-1000).

__-sa:__ Yerel ağdaki ana bilgisayarları keşfetmek için bir ARP taraması gerçekleştirin.

__-st:__ Hedefteki açık TCP bağlantı noktalarını tarayın.

__-su:__ Hedefteki açık UDP bağlantı noktalarını tarayın.


<br>

## Örnekler

1)
       netscout -ip=10.10.10.10 -st

2)
       netscout -ip=10.10.10.10/24 -sa

3)
       netscout -ip=10.10.10.10 -st -p=3306

4)
       netscout -ip=10.10.10.10 -st -pr=0-4000

5)
       netscout -ip=10.10.10.10 -su -p=9999

6)
       netscout -ip=10.10.10.10 -su -pr=0-4000