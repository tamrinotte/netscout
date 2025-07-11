# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from sys import exit as sysexit
from os import geteuid
from modules.logging_config import(
    debug,
    info,
)

##############################

# ROOT PRIVILEGES

##############################

def check_root_privileges():
    effective_user_id = geteuid()
    debug(f"Effective User ID: {effective_user_id}") 
    if effective_user_id != 0:
        print("[!] This scan requires root privileges.")
        info("Exiting the program due to lack of root privileges.")
        sysexit(1)