#!/bin/bash

# Get the username
username=${SUDO_USER:-${USER}}

# Change the file's ownership
chown $username:$username "/usr/bin/netscope"
