# NetScout
![NetScout](https://raw.githubusercontent.com/tamrinotte/netscout/go/app_images/netscout_logo.png)

NetScout is a port scanning tool that checks TCP ports on a specified IP address or range. It supports scanning single ports or port ranges, identifies open ports, and attempts to determine the associated service name. The tool runs scans concurrently for speed and provides a summary of open ports along with scan duration.

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

3) Start the installer.

       sudo dpkg -i netscout.deb

<br>

## Options

__-h, --help:__ Displays the help message.

__ip_address:__ Target IP address (e.g., 10.10.10.10).

__--port PORT:__ Port number (e.g., 1005).

__--port-range PORT:__ Port range (e.g., 0-4000).

<br>

## Examples

1)
       netscout 10.10.10.10

2)
       netscout 10.10.10.10 --port 3306

3)
       netscout 10.10.10.10 --port-range 0-4000

## References

1) Service Names and Port Numbers CSV File -> https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml

---

# NetScout
![NetScout](https://raw.githubusercontent.com/tamrinotte/netscout/go/app_images/netscout_logo.png)

NetScout, belirli bir IP adresi veya aralığındaki TCP bağlantı noktalarını kontrol eden bir bağlantı noktası tarama aracıdır. Tek bağlantı noktalarının veya bağlantı noktası aralıklarının taranmasını destekler, açık bağlantı noktalarını tanımlar ve ilişkili hizmet adını belirlemeye çalışır. Araç, hız için taramaları eşzamanlı olarak çalıştırır ve tarama süresiyle birlikte açık bağlantı noktalarının bir özetini sağlar.

<br>

## Kurulum

1) Yükleyiciyi indirin.

	- Kali

	      curl -L https://github.com/tamrinotte/netscout/releases/download/go_kali_v0.1.0/netscout.deb -o netscout.deb

	- Debian

	      curl -L https://github.com/tamrinotte/netscout/releases/download/go_debian_v0.1.0/netscout.deb -o netscout.deb

2) Yükleyiciyi başlatın.

       sudo dpkg -i netscout.deb

<br>

## Seçenekler

__-h, --help:__ Yardım mesajını görüntüler.

__ip_address:__ Hedef IP adresi (ör. 10.10.10.10).

__--port PORT:__ Bağlantı noktası numarası (ör. 1005).

__--port-range PORT:__ Bağlantı noktası aralığı (ör. 0-4000).

<br>

## Örnekler

1)
       netscout 10.10.10.10

2)
       netscout 10.10.10.10 --port 3306

3)
       netscout 10.10.10.10 --port-range 0-4000

## Kaynakça

1) Service Names and Port Numbers CSV Dosyası -> https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml