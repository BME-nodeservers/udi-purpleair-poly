#!/usr/bin/env python3
"""
Polyglot v3 node server Purple Air data
Copyright (C) 2020,2021 Robert Paauwe
"""

import udi_interface
import sys
import time
#import datetime
#import requests
#import socket
#import math
#import re
#import json
from nodes import sensor
#from datetime import timedelta

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class Controller(udi_interface.Node):
    id = 'controller'
    def __init__(self, polyglot, primary, address, name):
        super(Controller, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = name
        self.address = address
        self.primary = primary
        self.configured = False
        self.force = True
        self.sensor_list = {}
        self.in_config = False
        self.in_discover = False

        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')

        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, self.address)
        # TODO: sensor nodes should subscribe to POLL!
        #self.poly.subscribe(self.poly.POLL, self.poll)

        self.poly.ready()
        self.poly.addNode(self)

    # Process changes to customParameters
    def parameterHandler(self, params):
        self.configured = False
        discover = False
        self.Parameters.load(params)

        # How to detect that self.Parameters is empty?
        if len(self.Parameters) == 0:
            self.Notices['cfg'] = 'Enter sensor name and ID to configure.'
            return

        # parameters should be alist of sensor name / sensor id
        self.Notices.clear()
        for p in self.Parameters:
            self.configured = True
            LOGGER.info('Found Purple Air sensor ID {} with ID {}'.format(p, self.Parameters[p]))
            if p not in self.sensor_list:
                self.sensor_list[p] = {'id': self.Parameters[p], 'configured': False}
                discover = True
            elif self.Parameters.isChanged(p):
                self.sensor_list[p] = {'id': self.Parameters[p], 'configured': False}
                discover = True

        if discover:
            self.discover()


    def start(self):
        LOGGER.info('Starting node server')
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()

        if len(self.Parameters) == 0:
            self.Notices['cfg'] = 'Enter sensor name and ID to configure.'

        LOGGER.info('Node server started')

    # control node has nothing to query, can we remove this?
    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        # Create nodes for each sensor here
        LOGGER.info("In Discovery...")
        for sensor_name in self.sensor_list:
            LOGGER.debug(self.sensor_list[sensor_name])
            if self.sensor_list[sensor_name]['configured']:
                LOGGER.info('Sensor ' + sensor_name + ' already configured, skipping.')
                continue

            try:
                node = sensor.SensorNode(self.poly, self.address, self.sensor_list[sensor_name]['id'], sensor_name)
                node.configure(self.sensor_list[sensor_name]['id'])
                LOGGER.info('Adding new node for ' + sensor_name)
                self.poly.addNode(node)
                self.sensor_list[sensor_name]['configured'] = True
            except Exception as e:
                LOGGER.error(str(e))

    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    commands = {
            'UPDATE_PROFILE': update_profile,
            }

    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            ]


