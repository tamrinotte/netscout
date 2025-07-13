package modules

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

// ##############################
//
// # GLOBAL VARIABLES
//
// ##############################

var (
	servicePortMap = make(map[string]string) // key: "port/protocol"
	serviceOnce    sync.Once

	serviceProbes []Probe
	probesOnce    sync.Once
	probesErr     error
)

// Probe represents a service probe structure
type Probe struct {
	Port         int    `json:"port"`
	Protocol     string `json:"protocol"`
	ProbePayload string `json:"probe_payload"`
}

// ##############################
//
// # LOAD IANA SERVICE-NAMES CSV FILE
//
// ##############################

func LoadIanaServices(filePath string) error {
	var loadErr error

	serviceOnce.Do(func() {
		file, err := os.Open(filePath)
		if err != nil {
			loadErr = err
			return
		}
		defer file.Close()

		reader := csv.NewReader(file)
		headers, err := reader.Read()
		if err != nil {
			loadErr = err
			return
		}

		colIndex := make(map[string]int)
		for i, col := range headers {
			colIndex[strings.TrimSpace(col)] = i
		}

		for {
			record, err := reader.Read()
			if err != nil {
				break // EOF
			}

			serviceName := strings.TrimSpace(record[colIndex["Service Name"]])
			portStr := strings.TrimSpace(record[colIndex["Port Number"]])
			protocol := strings.ToLower(strings.TrimSpace(record[colIndex["Transport Protocol"]]))

			if serviceName == "" || portStr == "" || protocol == "" {
				continue
			}

			port, err := strconv.Atoi(portStr)
			if err != nil {
				continue
			}

			key := fmt.Sprintf("%d/%s", port, protocol)
			servicePortMap[key] = serviceName
		}
	})

	return loadErr
}

// ##############################
//
// # SERVICE NAME LOOKUP
//
// ##############################

func LookupServiceName(port int, protocol string) string {
	key := fmt.Sprintf("%d/%s", port, strings.ToLower(protocol))
	if service, exists := servicePortMap[key]; exists {
		return service
	}
	return "unknown"
}

// ##############################
//
// # LOAD SERVICE PROBES (JSON)
//
// ##############################

func LoadProbes(path string) ([]Probe, error) {
	probesOnce.Do(func() {
		data, err := os.ReadFile(path)
		if err != nil {
			probesErr = err
			return
		}

		err = json.Unmarshal(data, &serviceProbes)
		if err != nil {
			probesErr = err
			return
		}
	})
	return serviceProbes, probesErr
}

// ##############################
//
// # FIND SERVICE PROBE
//
// ##############################

func FindProbe(port int, protocol string) *Probe {
	probes, err := LoadProbes("data/service-probes.json")
	if err != nil {
		return nil
	}
	for _, probe := range probes {
		if probe.Port == port && strings.EqualFold(probe.Protocol, protocol) {
			return &probe
		}
	}
	return nil
}

// ##############################
//
// # DECODE PROBE PAYLOAD
//
// ##############################

func decodeProbePayload(payload string) ([]byte, error) {
	decodedStr, err := strconv.Unquote(`"` + payload + `"`)
	if err != nil {
		return nil, err
	}
	return []byte(decodedStr), nil
}

// ##############################
//
// # BANNER GRABBER
//
// ##############################

func GrabServiceBanner(conn net.Conn, timeout time.Duration, port int, protocol string) string {
	var banner strings.Builder

	_ = conn.SetDeadline(time.Now().Add(timeout))
	defer conn.SetDeadline(time.Time{})

	// Send optional probe payload
	if probe := FindProbe(port, protocol); probe != nil {
		payloadBytes, err := decodeProbePayload(probe.ProbePayload)
		if err == nil && len(payloadBytes) > 0 {
			_, _ = conn.Write(payloadBytes)
		}
	}

	buf := make([]byte, 4096)
	for {
		n, err := conn.Read(buf)
		if n > 0 {
			banner.Write(buf[:n])
		}
		if err != nil {
			break // EOF or timeout
		}
	}

	fullBanner := banner.String()

	// Extract HTTP headers if possible (everything before first double CRLF)
	headersEnd := strings.Index(fullBanner, "\r\n\r\n")
	if headersEnd != -1 {
		return strings.TrimSpace(fullBanner[:headersEnd])
	}

	// Fallback: return entire response if no header boundary found
	return strings.TrimSpace(fullBanner)
}