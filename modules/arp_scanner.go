package modules

import (
	"errors"
	"fmt"
	"log"
	"net"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/layers"
	"github.com/google/gopacket/pcap"
)

// ##############################
//
// # HELPER FUNCTIONS
//
// ##############################

func getInterfaceForNetwork(ipNet *net.IPNet) (*net.Interface, error) {
	ifaces, err := net.Interfaces()
	if err != nil {
		return nil, err
	}

	for _, iface := range ifaces {
		if iface.Flags&net.FlagUp == 0 || iface.Flags&net.FlagLoopback != 0 {
			continue
		}
		addrs, _ := iface.Addrs()
		for _, addr := range addrs {
			if ipNet.Contains(getIPFromAddr(addr)) {
				return &iface, nil
			}
		}
	}
	return nil, errors.New("no suitable interface found")
}

func getInterfaceIPv4Addr(iface *net.Interface) (net.IP, error) {
	addrs, err := iface.Addrs()
	if err != nil {
		return nil, err
	}
	for _, addr := range addrs {
		ip := getIPFromAddr(addr)
		if ip.To4() != nil {
			return ip, nil
		}
	}
	return nil, errors.New("no IPv4 address found")
}

func incrementIP(ip net.IP) {
	for j := len(ip) - 1; j >= 0; j-- {
		ip[j]++
		if ip[j] > 0 {
			break
		}
	}
}

func getIPFromAddr(addr net.Addr) net.IP {
	switch v := addr.(type) {
	case *net.IPNet:
		return v.IP
	case *net.IPAddr:
		return v.IP
	}
	return nil
}

// ##############################
//
// # RUN ARP SCAN
//
// ##############################

func RunArpScan(targetCIDR string) {
	// Check if the network is IPv4 and parse it
	_, ipv4Net, err := net.ParseCIDR(targetCIDR)
	if err != nil {
		log.Fatalf("[!] Invalid CIDR notation: %v", err)
	}
	if ipv4Net.IP.To4() == nil {
		log.Fatalln("[!] ARP scan only supports IPv4 addresses.")
	}

	fmt.Println("=== ARP Scan ===")
	fmt.Printf("[*] Performing ARP scan on %s...\n", ipv4Net.String())

	// Find network interface
	iface, err := getInterfaceForNetwork(ipv4Net)
	if err != nil {
		log.Fatalf("[!] Could not find interface for %s: %v", ipv4Net.String(), err)
	}

	// Open live pcap handle
	handle, err := pcap.OpenLive(iface.Name, 65536, false, pcap.BlockForever)
	if err != nil {
		log.Fatalf("[!] Failed to open device %s: %v", iface.Name, err)
	}
	defer handle.Close()

	start := time.Now()

	srcMAC := iface.HardwareAddr
	srcIP, err := getInterfaceIPv4Addr(iface)
	if err != nil {
		log.Fatalf("[!] Failed to get source IP: %v", err)
	}

	// Build ARP request packet
	for ip := ipv4Net.IP.Mask(ipv4Net.Mask); ipv4Net.Contains(ip); incrementIP(ip) {
		if ip.Equal(srcIP) {
			continue // skip own IP
		}

		eth := layers.Ethernet{
			SrcMAC:       srcMAC,
			DstMAC:       net.HardwareAddr{0xff, 0xff, 0xff, 0xff, 0xff, 0xff},
			EthernetType: layers.EthernetTypeARP,
		}

		arp := layers.ARP{
			AddrType:          layers.LinkTypeEthernet,
			Protocol:          layers.EthernetTypeIPv4,
			HwAddressSize:     6,
			ProtAddressSize:   4,
			Operation:         layers.ARPRequest,
			SourceHwAddress:   []byte(srcMAC),
			SourceProtAddress: []byte(srcIP.To4()),
			DstHwAddress:      []byte{0, 0, 0, 0, 0, 0},
			DstProtAddress:    []byte(ip.To4()),
		}

		buf := gopacket.NewSerializeBuffer()
		opts := gopacket.SerializeOptions{}
		gopacket.SerializeLayers(buf, opts, &eth, &arp)

		if err := handle.WritePacketData(buf.Bytes()); err != nil {
			log.Printf("[!] Failed to send ARP request: %v\n", err)
		}
	}

	// Capture ARP replies
	packetSource := gopacket.NewPacketSource(handle, handle.LinkType())
	timeout := time.After(4 * time.Second)
	fmt.Println("\n[*] Hosts found:")

foundLoop:
	for {
		select {
		case packet := <-packetSource.Packets():
			if arpLayer := packet.Layer(layers.LayerTypeARP); arpLayer != nil {
				arp, _ := arpLayer.(*layers.ARP)
				if arp.Operation == layers.ARPReply {
					fmt.Printf("IP Address: %s - MAC Address: %s\n",
						net.IP(arp.SourceProtAddress).String(),
						net.HardwareAddr(arp.SourceHwAddress).String())
				}
			}
		case <-timeout:
			break foundLoop
		}
	}

	elapsed := time.Since(start)
	fmt.Printf("\nDuration: %.2f seconds\n", elapsed.Seconds())
}