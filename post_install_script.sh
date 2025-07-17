#!/bin/bash

main() {
    declare_variables
    set_up_file_ownerships
    app_name="netscout"
}

declare_variables() {
    username=${SUDO_USER:-${USER}}
}

set_up_file_ownerships() {
    chown -R $username:$username "/opt/$appname/"
    chown $username:$username "/usr/bin/$appname"
}

main