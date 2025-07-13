package modules

import (
	"fmt"
	"os"
	"syscall"
)

// ##############################
//
// # ROOT PRIVILEGES
//
// ##############################

func CheckRootPrivileges() {
	euid := syscall.Geteuid()
	fmt.Printf("[DEBUG] Effective User ID: %d\n", euid)

	if euid != 0 {
		fmt.Println("[!] This scan requires root privileges.")
		fmt.Println("[INFO] Exiting the program due to lack of root privileges.")
		os.Exit(1)
	}
}