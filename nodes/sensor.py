#!/usr/bin/env python3
"""
Polyglot v3 node server Purple Air data
Copyright (C) 2020,2021 Robert Paauwe
"""

import udi_interface
import requests
import json

LOGGER = udi_interface.LOGGER

class SensorNode(udi_interface.Node):
    # class variables
    id = 'aqi'
    status= None

    def __init__(self, polyglot, primary, address, name):
        # call the default init
        super(SensorNode, self).__init__(polyglot, primary, address, name)

        self.host = ''
        self.headers = ''
        self.configured = False;
        self.uom = {
                'CLITEMP' : 17,
                'CLIHUM' : 22,
                'BARPRES' : 117,
                'GV0' : 122,
                'GV1' : 45,
                'GV3' : 122,
                'GV4' : 122,
                'GV5' : 122,
                'GV6' : 122,
                'GV7' : 122,
                'GV8' : 122,
                'GV10' : 56,
                'GV11' : 25,
                'GV12' : 51,
                }

        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, address)


    drivers = [
            {'driver': 'CLITEMP', 'value': 0, 'uom': 17, 'name':'Temperature'},  # temperature
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22, 'name':'Humidity'},   # humidity
            {'driver': 'BARPRES', 'value': 0, 'uom': 117, 'name':'Pressure'}, # pressure
            {'driver': 'GV0', 'value': 0, 'uom': 56, 'name':'Current PM 2.5'}, # current PM2.5
            {'driver': 'GV1', 'value': 0, 'uom': 45, 'name':'Age'},      # age in minutes
            {'driver': 'GV3', 'value': 0, 'uom': 56, 'name':'10 min Avg'},      # 10 min avg
            {'driver': 'GV4', 'value': 0, 'uom': 56, 'name':'30 min Avg'},      # 30 min avg
            {'driver': 'GV5', 'value': 0, 'uom': 56, 'name':'60 min Avg'},      # 60 min avg
            {'driver': 'GV6', 'value': 0, 'uom': 56, 'name':'6 hour Avg'},      # 6 hr avg
            {'driver': 'GV7', 'value': 0, 'uom': 56, 'name':'24 hour Avg'},      # 24 hr avg
            {'driver': 'GV8', 'value': 0, 'uom': 56, 'name':'1 week Avg'},      # 1 week avg
            {'driver': 'GV10', 'value': 0, 'uom': 56, 'name':'EPA AQI'},     # AQI
            {'driver': 'GV11', 'value': 0, 'uom': 25, 'name':'AQI String'},     # AQI string
            {'driver': 'GV12', 'value': 0, 'uom': 51, 'name':'Data Confidence'},     # confidence
            ]


    def start(self):
        self.poll('shortPoll')

    def configure(self, sensor, apikey):
        fields='fields=name,model,temperature,humidity,pressure,pm2.5,pm2.5_10minute,pm2.5_30minute,pm2.5_60minute, pm2.5_6hour, pm2.5_24hour, pm2.5_1week,confidence,last_seen'

        self.host = 'https://api.purpleair.com/v1/sensors/' + sensor + '?' + fields
        self.headers = {'X-API-Key':apikey}
        self.configured = True

    def update_driver(self, driver, value, force=False, prec=3):
        try:
            if value == None or value == "None":
                value = "0"
            self.setDriver(driver, round(float(value), prec), True, force, self.uom[driver])
            LOGGER.debug('setDriver (%s, %f)' %(driver, float(value)))
        except:
            LOGGER.warning('Missing data for driver ' + driver)

    def epa_aqi(self, pm25):
        aqi = 0
        breakpoints = [
                [0, 12],
                [12.1, 35.4],
                [35.5, 55.4],
                [55.5, 150.4],
                [150.5, 250.4],
                [250.5, 500.4],
                ]
        indexes = [
                [0, 50],
                [51, 100],
                [101, 150],
                [151, 200],
                [201, 300],
                [301, 500],
                ]

        pm25 = round(pm25,1)

        # find the breakpoints for the pm25 value
        try:
            for bpi in range(0,6):
                if pm25 >= breakpoints[bpi][0] and pm25 <= breakpoints[bpi][1]:
                    break
        except Exception as e:
            LOGGER.error('AQI_bp: ' + str(e))
        
        if bpi == 6:
            LOGGER.error('AQI out of range!')
            return

        try:
            aqi = ((indexes[bpi][1] - indexes[bpi][0]) / (breakpoints[bpi][1] - breakpoints[bpi][0])) * (pm25 - breakpoints[bpi][0]) + indexes[bpi][0]
        except Exception as e:
            LOGGER.error('AQI_calc: ' + str(e))

        LOGGER.debug('Calculated AQI = ' + str(aqi))
        return (round(aqi, 0), indexes[bpi][0])

    # This is no longer used with the new API and the confidence value is
    # provided for us.
    def calculate_confidence(self, results):
        channel_a = results[0]
        channel_b = results[1]

        if 'AGE' in channel_a and 'AGE' in channel_b:
            if channel_a['AGE'] != channel_b['AGE']:
                LOGGER.error('data channels age differs, bad data!')
                return 0
        else:
            LOGGER.error('missing data age info.')
            return 0

        if 'PM2_5Value' in channel_a and 'PM2_5Value' in channel_b:
            A = float(channel_a['PM2_5Value'])
            B = float(channel_b['PM2_5Value'])

            C = 100 - abs(((A - B) / (A + B)) * 100)
            return round(C, 0)
        else:
            LOGGER.error('missing data for PM2.5.')
            return 0


    def poll(self, polltype):
        # Query for the current air quality conditions. We can do this fairly
        # frequently, probably as often as once a minute.
        if polltype is not 'shortPoll':
            return

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        try:
            c = requests.get(self.host, headers=self.headers)
            try:
                jdata = c.json()
            except:
                LOGGER.error('Connection issue: ' + str(c))
                c.close()
                return

            c.close()
            LOGGER.debug(jdata)

            if jdata == None:
                LOGGER.error('Current condition query returned no data')
                return

            '''
            new API data format is completely different from what we have below.
            need to re-write this to parse it now.....
            '''
            sensor = jdata['sensor']

            if 'name' in sensor:
                LOGGER.info('Air Quality data for ' + sensor['name'])
            if 'model' in sensor:
                LOGGER.info('Air Quality sensor type ' + sensor['model'])

            if 'pm2.5' in sensor:
                self.update_driver('GV0', sensor['pm2.5'])

            if 'confidence' in sensor:
                LOGGER.info('Data confidence level = ' + str(sensor['confidence']) + '%')
                self.update_driver('GV12', sensor['confidence'])
            if 'temperature' in sensor:
                self.update_driver('CLITEMP', sensor['temperature'])
            if 'humidity' in sensor:
                self.update_driver('CLIHUM', sensor['humidity'])
            if 'pressure' in sensor:
                self.update_driver('BARPRES', sensor['pressure'])

            # age is difference between jdata[time_stamp] and sensor['last_seen']
            #  in minutes
            if 'time_stamp' in jdata and 'last_seen' in sensor:
                age = (jdata['time_stamp'] - sensor['last_seen']) / 60 
                self.update_driver('GV1', age)

            # These are different from old API.  
            # {"pm2.5" : 1.6,
            #   "pm2.5_10minute" : 1.2, 
            #   "pm2.5_30minute" : 1.4, 
            #   "pm2.5_60minute" : 1.5,
            #   "pm2.5_6hour" : 1.9,
            #   "pm2.5_24hour" : 1.5,
            #   "pm2.5_1week" : 2.4,
            #   "time_stamp" : 1654455846},

            LOGGER.error('Loading stats')
            if 'stats' in sensor:
                stats = sensor['stats']
                if 'pm2.5_10minute' in stats:
                    self.update_driver('GV3', stats['pm2.5_10minute'])
                    (aqi, idx) = self.epa_aqi(float(stats['pm2.5_10minute']))
                    self.update_driver('GV10', aqi)
                    self.update_driver('GV11', idx)
                if 'pm2.5_30minute' in stats:
                    self.update_driver('GV4', stats['pm2.5_30minute'])
                if 'pm2.5_60minute' in stats:
                    self.update_driver('GV5', stats['pm2.5_60minute'])
                if 'pm2.5_6hour' in stats:
                    self.update_driver('GV6', stats['pm2.5_6hour'])
                if 'pm2.5_24hour' in stats:
                    self.update_driver('GV7', stats['pm2.5_24hour'])
                if 'pm2.5_1week' in stats:
                    self.update_driver('GV8', stats['pm2.5_1week'])
            
        except Exception as e:
            LOGGER.error('Current observation update failure')
            LOGGER.error(e)

    def query(self, cmd=None):
        self.poll('shortPoll')

    commands = {
            'QUERY': query,
            }
