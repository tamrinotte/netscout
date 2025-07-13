package main

import (
	"flag"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"netscout/modules"
)

// ##############################
//
// # HELPER FUNCTIONS
//
// ##############################

func parsePortRange(rangeStr string) ([]int, error) {
	parts := strings.Split(rangeStr, "-")
	if len(parts) != 2 {
		return nil, fmt.Errorf("invalid port range format. Use <start>-<end>")
	}
	start, err1 := strconv.Atoi(parts[0])
	end, err2 := strconv.Atoi(parts[1])
	if err1 != nil || err2 != nil {
		return nil, fmt.Errorf("invalid number in port range")
	}
	if start < 0 || end > 65535 || start > end {
		return nil, fmt.Errorf("port range must be within 0-65535 and start <= end")
	}

	ports := make([]int, 0, end-start+1)
	for i := start; i <= end; i++ {
		ports = append(ports, i)
	}
	return ports, nil
}

// ##############################
//
// # MAIN
//
// ##############################

func main() {
	ipAddress := flag.String("ip", "", "Target IP address.")
	singlePort := flag.Int("p", -1, "Target port (e.g., -p=22).")
	portRange := flag.String("pr", "", "Target port range (e.g., -pr=0-1000).")
	arpScan := flag.Bool("sa", false, "Perform an ARP scan to discover hosts on the local network.")
	tcpScan := flag.Bool("st", false, "Scan for open TCP ports on the target.")
	udpScan := flag.Bool("su", false, "Scan for open UDP ports on the target.")
	flag.Usage = func() {
		fmt.Println("Usage: netscout [flags]")
		flag.PrintDefaults()
		fmt.Println("\nExamples:")
		fmt.Println("  netscout -ip=10.10.10.10 -st")
		fmt.Println("  netscout -ip=10.10.10.10/24 -sa")
		fmt.Println("  netscout -ip=10.10.10.10 -st -p=3306")
		fmt.Println("  netscout -ip=10.10.10.10 -st -pr=0-4000")
		fmt.Println("  netscout -ip=10.10.10.10 -su -p=9999")
		fmt.Println("  netscout -ip=10.10.10.10 -su -pr=0-4000")
	}
	flag.Parse()

	if *ipAddress == "" {
		fmt.Println("Error: -ip is required.")
		flag.Usage()
		os.Exit(1)
	}

	// Enforce mutual exclusivity of scan modes
	selectedCountScanGroup := 0
	if *arpScan {
		selectedCountScanGroup++
	}
	if *tcpScan {
		selectedCountScanGroup++
	}
	if *udpScan {
		selectedCountScanGroup++
	}
	if selectedCountScanGroup == 0 {
		fmt.Println("Error: At least one of -sa, -st, or -su must be specified.")
		flag.Usage()
		os.Exit(1)
	}
	if selectedCountScanGroup > 1 {
		fmt.Println("Error: Only one of -sa, -st, or -su can be specified at a time.")
		flag.Usage()
		os.Exit(1)
	}

	// Enforce mutual exclusivity of port specs if scanning ports
	selectedCountPortSpec := 0
	if *singlePort != -1 {
		selectedCountPortSpec++
	}
	if *portRange != "" {
		selectedCountPortSpec++
	}
	if selectedCountPortSpec > 1 {
		fmt.Println("Error: Only one of -p or -pr can be specified.")
		flag.Usage()
		os.Exit(1)
	}

	// Prepare ports list
	var ports []int
	if *singlePort != -1 {
		if *singlePort < 0 || *singlePort > 65535 {
			fmt.Println("Error: Port must be between 0-65535.")
			os.Exit(1)
		}
		ports = []int{*singlePort}
	} else if *portRange != "" {
		parsedPorts, err := parsePortRange(*portRange)
		if err != nil {
			fmt.Println("Error:", err)
			os.Exit(1)
		}
		ports = parsedPorts
	} else {
		// Default ports
		for i := 0; i <= 1000; i++ {
			ports = append(ports, i)
		}
	}

	// Max threads constant (same as Python version)
	const maxThreads = 100

	// Run requested modules
	if *arpScan {
		modules.RunArpScan(*ipAddress)
	}

	if *tcpScan {
		// Load IANA service name-port mapping before any TCP scan
		csvPath := "data/service-names-port-numbers.csv"
		if err := modules.LoadIanaServices(csvPath); err != nil {
			fmt.Printf("[!] Could not load service names CSV (%s): %v\n", csvPath, err)
		}

		modules.RunTcpScan(*ipAddress, ports, maxThreads)
	}

	if *udpScan {
		modules.CheckRootPrivileges()
		timeout := 5 * time.Second
		quiet := 3 * time.Second
		maxWait := 10 * time.Second
		modules.RunUDPScan(*ipAddress, ports, maxThreads, timeout, quiet, maxWait)
	}
}