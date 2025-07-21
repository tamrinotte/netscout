// Note: You  most recently foundout that the problem were facing was a 
// race condition problem that was rising from poor usage of goroutines.
// After you replaced goroutines with a regular old loop, false positives are disappeared.
// TODO: You need to utilize goroutines correctly to increase the tools performance.
package modules

import (
	"fmt"
	"net"
	"sync"
	"time"
)

// ##############################
//
// # CUSTOM DATA TYPE
//
// ##############################

type UDPScanResult struct {
	Port        int
	ServiceName string
	IsOpen      bool
	UDPResponse string
}

// ##############################
//
// # SCAN A PORT
//
// ##############################

func scanUDPPort(target string, port int, timeout time.Duration) UDPScanResult {
	addr := fmt.Sprintf("%s:%d", target, port)
	service := LookupServiceName(port, "udp")
	res := UDPScanResult{Port: port, ServiceName: service}

	conn, err := net.DialTimeout("udp", addr, timeout)
	if err != nil {
		return res
	}
	defer conn.Close()

	conn.SetDeadline(time.Now().Add(timeout))
	conn.Write([]byte{})

	buf := make([]byte, 4096)
	n, err := conn.Read(buf)
	if err == nil && n > 0 {
		res.IsOpen = true
		res.UDPResponse = string(buf[:n])
	}
	return res
}

// ##############################
//
// # SCAN PORTS
//
// ##############################

func RunUDPScan(
	target string,
	ports []int,
	_ int, // maxWorkers ignored now
	timeout, quietTimeout, maxWait time.Duration,
) {
	fmt.Println("=== UDP Scan ===")
	fmt.Printf("[*] Performing UDP scan for %s\n\n", target)
	
	LoadIanaServices("data/service-names-port-numbers.csv")

	closedCh := make(chan int, len(ports))
	stopICMP := make(chan struct{})
	var icmpWG sync.WaitGroup
	closedMap := make(map[int]struct{})
	var closedMu sync.Mutex

	icmpWG.Add(1)
	go ListenICMP(target, closedCh, stopICMP, &icmpWG)

	// Wait a bit to ensure ICMP listener is ready
	time.Sleep(200 * time.Millisecond)

	go func() {
		for p := range closedCh {
			closedMu.Lock()
			closedMap[p] = struct{}{}
			closedMu.Unlock()
		}
	}()

	resultsCh := make(chan UDPScanResult, len(ports))

	// Sequential scanning loop with delay
	for _, port := range ports {
		res := scanUDPPort(target, port, timeout)
		resultsCh <- res
		time.Sleep(1 * time.Second) // 1 second delay between probes
	}
	close(resultsCh)

	// Wait for late ICMP replies (quietTimeout or maxWait)
	start := time.Now()
	lastICMP := time.Now()

loop:
	for {
		select {
		case p := <-closedCh:
			closedMu.Lock()
			closedMap[p] = struct{}{}
			closedMu.Unlock()
			lastICMP = time.Now()

		case <-time.After(quietTimeout):
			if time.Since(lastICMP) >= quietTimeout {
				break loop
			}
		}
		if time.Since(start) >= maxWait {
			break
		}
	}

	close(stopICMP)
	icmpWG.Wait()
	close(closedCh)

	// Now classify results only after all ICMP verdicts processed
	var openReplies []UDPScanResult
	var openFiltered []int

	for res := range resultsCh {
		closedMu.Lock()
		_, wasClosed := closedMap[res.Port]
		closedMu.Unlock()

		if wasClosed {
			// skip closed ports
			continue
		}
		if res.IsOpen {
			openReplies = append(openReplies, res)
		} else {
			openFiltered = append(openFiltered, res.Port)
		}
	}

	// print results
	if len(openReplies) > 0 {
		fmt.Println("Open UDP ports (received UDP reply):")
		for _, r := range openReplies {
			fmt.Printf("Port: %d\nService: %s\nProtocol: udp\n", r.Port, r.ServiceName)
			if r.UDPResponse != "" {
				fmt.Printf("UDP reply: %s\n", r.UDPResponse)
			}
			fmt.Println("State: Open\n")
		}
	}

	if len(openFiltered) > 0 {
		fmt.Println("UDP ports open|filtered (no response):")
		for _, p := range openFiltered {
			svc := LookupServiceName(p, "udp")
			fmt.Printf("Port: %d\nService: %s\nProtocol: udp\nState: Open|Filtered\n\n", p, svc)
		}
	}

	fmt.Println("UDP scan completed.")
}