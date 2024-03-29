#!/usr/bin/env python3
"""
Polyglot v3 node server Purple Air data
Copyright (C) 2020,2021,2023 Robert Paauwe
"""

import udi_interface
import sys
import time
from nodes import purpleair

VERSION = '2.1.3'
LOGGER = udi_interface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([purpleair.Controller])
        LOGGER.info('Starting PurpleAir Plug-in version {}'.format(VERSION))
        polyglot.start(VERSION)
        control = purpleair.Controller(polyglot, "controller", "controller", "Purple Air AQI")
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

