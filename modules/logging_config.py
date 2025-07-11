# This Python file uses the following encoding: utf-8

# MODULES AND/OR LIBRARIES
from logging import (
    basicConfig,
    DEBUG,
    CRITICAL,
    disable,
    debug,
    info,
    error,
)

##############################

# LOGGING CONFIG

##############################

basicConfig(level=DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
disable(CRITICAL)
