package modules

import (
	"fmt"
	"net"
	"sync"
	"time"
)

// ##############################
//
// # STRUCTS
//
// ##############################

type TcpScanResult struct {
	Port         int
	ServiceName  string
	IsOpen       bool
	Banner       string
	ErrorMessage string
}

// ##############################
//
// # SINGLE PORT SCAN
//
// ##############################

func scanTcpPort(target string, port int, timeout time.Duration) TcpScanResult {
	address := fmt.Sprintf("%s:%d", target, port)
	conn, err := net.DialTimeout("tcp", address, timeout)
	if err != nil {
		return TcpScanResult{
			Port:         port,
			ServiceName:  LookupServiceName(port, "tcp"),
			IsOpen:       false,
			ErrorMessage: err.Error(),
		}
	}
	defer conn.Close()

	// Banner grab with optional probe
	banner := GrabServiceBanner(conn, 2*time.Second, port, "tcp")

	return TcpScanResult{
		Port:        port,
		ServiceName: LookupServiceName(port, "tcp"),
		IsOpen:      true,
		Banner:      banner,
	}
}

// ##############################
//
// # TCP SCAN MAIN FUNCTION
//
// ##############################

func RunTcpScan(target string, ports []int, maxThreads int) {
	// Load IANA service name-port mapping before any TCP scan
	csvPath := "/opt/netscout/data/service-names-port-numbers.csv"
	if err := LoadIanaServices(csvPath); err != nil {
		fmt.Printf("[!] Could not load service names CSV (%s): %v\n", csvPath, err)
	}

	fmt.Println("=== TCP Scan ===")
	fmt.Printf("[*] Target: %s\n", target)

	startTime := time.Now()
	var wg sync.WaitGroup
	sem := make(chan struct{}, maxThreads)

	for _, port := range ports {
		wg.Add(1)
		sem <- struct{}{}

		go func(p int) {
			defer wg.Done()
			address := fmt.Sprintf("%s:%d", target, p)
			conn, err := net.DialTimeout("tcp", address, 2*time.Second)
			if err != nil {
				<-sem
				return
			}
			defer conn.Close()

			// Lookup service name via service_recon.go
			service := LookupServiceName(p, "tcp")

			// Banner grab via service_recon.go
			banner := GrabServiceBanner(conn, 2*time.Second, p, "tcp")

			fmt.Printf("Port: %d\n", p)
			fmt.Printf("Protocol: tcp\n")
			fmt.Printf("Service: %s\n", service)
			if banner != "" {
				fmt.Printf("Banner: %s\n", banner)
			}
			fmt.Println("State: Open\n")

			<-sem
		}(port)
	}

	wg.Wait()

	duration := time.Since(startTime)
	fmt.Printf("[*] Duration: %.2f seconds\n", duration.Seconds())
}