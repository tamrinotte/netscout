package modules

import (
	"encoding/binary"
	"fmt"
	"net"
	"sync"
	"time"
)

const (
	ICMPTypeDestinationUnreachable = 3
	ICMPCodePortUnreachable        = 3
)

// ListenICMP listens for ICMP Port Unreachable messages and reports closed UDP ports
func ListenICMP(targetIP string, closedCh chan<- int, stop <-chan struct{}, wg *sync.WaitGroup) {
    defer wg.Done()

    conn, err := net.ListenPacket("ip4:icmp", "0.0.0.0")
    if err != nil {
        fmt.Printf("[!] Error creating ICMP listener: %v\n", err)
        return
    }
    defer conn.Close()

    buf := make([]byte, 1500)
    for {
        select {
        case <-stop:
            return
        default:
            conn.SetReadDeadline(time.Now().Add(1 * time.Second))
            n, addr, err := conn.ReadFrom(buf)
            if err != nil {
                if ne, ok := err.(net.Error); ok && ne.Timeout() {
                    continue
                }
                fmt.Printf("[!] ICMP read error: %v\n", err)
                continue
            }

            fmt.Printf("[DEBUG] Received ICMP packet from %s (%d bytes)\n", addr.String(), n)

			// With this:
			if addr.String() != targetIP {
				fmt.Printf("[DEBUG] Skipping ICMP from unexpected IP: %s\n", addr.String())
				continue
			}

            if n < 8+20+4 {
                fmt.Printf("[DEBUG] Packet too short (%d bytes) for ICMP + IP + UDP headers\n", n)
                continue
            }

            icmpType := buf[0]
            icmpCode := buf[1]
            fmt.Printf("[DEBUG] ICMP Type: %d, Code: %d\n", icmpType, icmpCode)

            if icmpType != ICMPTypeDestinationUnreachable || icmpCode != ICMPCodePortUnreachable {
                continue
            }

            ipHdrLen := int(buf[8]&0x0F) * 4
            udpStart := 8 + ipHdrLen
            if n < udpStart+4 {
                fmt.Printf("[DEBUG] Packet too short (%d bytes) for embedded UDP header\n", n)
                continue
            }

            // For better debugging print raw bytes of embedded IP header and UDP header
            fmt.Printf("[DEBUG] Embedded IP header bytes: % x\n", buf[8:8+ipHdrLen])
            fmt.Printf("[DEBUG] Embedded UDP header bytes: % x\n", buf[udpStart:udpStart+8])

            dstPort := int(binary.BigEndian.Uint16(buf[udpStart+2 : udpStart+4]))
            fmt.Printf("[DEBUG] Parsed destination UDP port: %d\n", dstPort)

            select {
            case closedCh <- dstPort:
                fmt.Printf("[DEBUG] Sent port %d to closedCh\n", dstPort)
            default:
                fmt.Printf("[DEBUG] closedCh full, dropped port %d\n", dstPort)
            }
        }
    }
}
