#!/bin/bash

main() {
    declare_variables
    set_up_file_ownerships
}

declare_variables() {
    username=${SUDO_USER:-${USER}}
    app_name="netscout"
}

set_up_file_ownerships() {
    chown -R $username:$username "/opt/$app_name/"
}

main