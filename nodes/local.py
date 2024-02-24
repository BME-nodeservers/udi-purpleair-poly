#!/usr/bin/env python3
"""
Polyglot v3 node server Purple Air data
Copyright (C) 2020,2021,2023 Robert Paauwe
"""

import udi_interface
import requests
import json

LOGGER = udi_interface.LOGGER

class LocalSensorNode(udi_interface.Node):
    # class variables
    id = 'laqi'
    status= None

    def __init__(self, polyglot, primary, address, name):
        # call the default init
        super(LocalSensorNode, self).__init__(polyglot, primary, address, name)

        self.host = ''
        self.headers = ''
        self.configured = False;
        self.uom = {
                'CLITEMP' : 17,
                'CLIHUM' : 22,
                'BARPRES' : 117,
                'DEWPT' : 17,
                'AQI' : 56,
                'PM25' : 122,
                'PM10' : 122,
                'GV0' : 122,
                'GV1' : 45,
                'GV2' : 56,
                'GV3' : 56,
                'GV4' : 56,
                'GV5' : 56,
                'GV6' : 56,
                'GV7' : 56,
                'GV8' : 56,
                'GV9' : 56,
                'GV10' : 56,
                'GV11' : 25,
                'GV12' : 51,
                }

        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, address)


    drivers = [
            {'driver': 'CLITEMP', 'value': 0, 'uom': 17, 'name':'Temperature' },  # temperature
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22, 'name':'Humidity' },      # humidity
            {'driver': 'BARPRES', 'value': 0, 'uom': 117, 'name':'Pressure' },    # pressure
            {'driver': 'DEWPT', 'value': 0, 'uom': 17, 'name':'Dewpoint' },       # dewpoint
            {'driver': 'PM25', 'value': 0, 'uom': 122, 'name':'PM 2.5' },         # PM2.5
            {'driver': 'PM10', 'value': 0, 'uom': 122, 'name':'PM 1.0' },         # PM1.0
            {'driver': 'GV0', 'value': 0, 'uom': 122, 'name':'PM 10' },           # PM10
            {'driver': 'AQI', 'value': 0, 'uom': 56, 'name':'EPA AQI' },          # AQI
            {'driver': 'GV11', 'value': 0, 'uom': 25, 'name':'EPA AQI string' },  # AQI string
            {'driver': 'GV12', 'value': 0, 'uom': 51, 'name':'Data Confidence' }, # confidence
            ]
    '''
            {'driver': 'GV1', 'value': 0, 'uom': 45},      # age in minutes
            {'driver': 'GV3', 'value': 0, 'uom': 56},      # 10 min avg
            {'driver': 'GV4', 'value': 0, 'uom': 56},      # 30 min avg
            {'driver': 'GV5', 'value': 0, 'uom': 56},      # 60 min avg
            {'driver': 'GV6', 'value': 0, 'uom': 56},      # 6 hr avg
            {'driver': 'GV7', 'value': 0, 'uom': 56},      # 24 hr avg
            {'driver': 'GV8', 'value': 0, 'uom': 56},      # 1 week avg
    '''


    def start(self):
        self.poll('shortPoll')

    def configure(self, sensor):
        self.host = 'http://{}/json?live=true'.format(sensor)
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

    # calculate the confidence by comparing PM2.5 channel A and channel B values
    def calculate_confidence(self, channel_a, channel_b):

        try:
            C = 100 - abs(((channel_a - channel_b) / (channel_a + channel_b)) * 100)
        except Exception as e:
            LOGGER.info('Both channels show 0 particulate matter, is this sensor working correctly?')
            C = 100

        return round(C, 0)


    def poll(self, polltype):
        # Query for the current air quality conditions. We can do this fairly
        # frequently, probably as often as once a minute.
        if polltype != 'shortPoll':
            return

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        try:
            c = requests.get(self.host)
            try:
                jdata = c.json()
            except:
                LOGGER.error('Connection issue: ' + str(c))
                c.close()
                return

            c.close()
            LOGGER.debug(jdata)

            if jdata == None:
                LOGGER.error('Sensor query returned no data')
                return

            '''
            Local query returns data in a different format from the API
            query.  Current documentation is somewhat limited.
            '''

            # we have sensor ID and location
            if 'SensorId' in jdata:
                LOGGER.info('Air Quality data for ' + jdata['SensorId'])

            # pm2.5_aqi and pm2.5_aqi_b.  p_2_5_um,  pm2_5_cf_1, p25aqic, 
            # p25aqic_b.  What's the difference between cf and atm for
            # particulate mass?
            #  CF=1 is for indoor data
            #  ATM is for outdoor data
            # so we need to look at the 'place' field to determine which 
            # to use.

            # status values for PM10 and PM25
            if 'place' in jdata:
                laqi = 0
                if jdata['place'] == 'outside':
                    # using ATM data
                    if 'pm2_5_atm' in jdata and 'pm2_5_atm_b' in jdata:
                        pm25 = (jdata['pm2_5_atm'] + jdata['pm2_5_atm_b']) / 2
                        self.update_driver('PM25', round(pm25, 2))

                        (aqi, idx) = self.epa_aqi(pm25)
                        self.update_driver('GV11', idx)

                        confidence = self.calculate_confidence(jdata['pm2_5_atm'], jdata['pm2_5_atm_b'])
                        LOGGER.info('Data confidence level = {}%'.format(confidence))
                        self.update_driver('GV12', confidence)
                    if 'pm1_0_atm' in jdata and 'pm1_0_atm_b' in jdata:
                        pm10 = (jdata['pm1_0_atm'] + jdata['pm1_0_atm_b']) / 2
                        self.update_driver('PM10', round(pm10, 2))
                    if 'pm10_0_atm' in jdata and 'pm10_0_atm_b' in jdata:
                        pm10 = (jdata['pm10_0_atm'] + jdata['pm10_0_atm_b']) / 2
                        self.update_driver('GV0', round(pm10, 2))
                    if 'pm2.5_aqi' in jdata and 'pm2.5_aqi_b' in jdata:
                        laqi = (jdata['pm2.5_aqi'] + jdata['pm2.5_aqi_b']) / 2
                        self.update_driver('AQI', round(laqi, 0))

                    LOGGER.info('AQI: {} vs. {} {}'.format(aqi, laqi, idx))
                else: # indoor sensor
                    # using CF data
                    if 'pm2_5_cf_1' in jdata  and 'pm2_5_cf_1_b' in jdata:
                        pm25 = (jdata['pm2_5_cf_1'] + jdata['pm2_5_cf_1_b']) / 2
                        self.update_driver('PM25', round(pm25, 2))

                        (aqi, idx) = self.epa_aqi(pm25)
                        self.update_driver('GV11', idx)

                        confidence = self.calculate_confidence(jdata['pm2_5_cf_1'], jdata['pm2_5_cf_1_b'])
                        LOGGER.info('Data confidence level = {}%'.format(confidence))
                        self.update_driver('GV12', confidence)
                    elif 'pm2_5_cf_1' in jdata:
                        pm25 = jdata['pm2_5_cf_1']
                        self.update_driver('PM25', round(pm25, 2))

                        (aqi, idx) = self.epa_aqi(pm25)
                        self.update_driver('GV11', idx)
                        self.update_driver('GV12', 100)
                    if 'pm1_0_cf_1' in jdata:
                        pm10 = (jdata['pm1_0_cf_1'] + jdata['pm1_0_cf_1_b']) / 2
                        self.update_driver('PM10', round(pm10, 2))
                    elif 'pm1_0_cf_1' in jdata:
                        self.update_driver('PM10', round(jdata['pm1_0_cf_1'], 2))
                    if 'pm10_0_cf_1' in jdata and 'pm10_0_cf_1_b' in jdata:
                        pm10 = (jdata['pm10_0_cf_1'] + jdata['pm10_0_cf_1_b']) / 2
                        self.update_driver('GV0', round(pm10, 2))
                    elif 'pm01_0_cf_1' in jdata:
                        self.update_driver('GV0', round(jdata['pm01_0_cf_1'], 2))
                    if 'pm2.5_aqi' in jdata and 'pm2.5_aqi_b' in jdata:
                        laqi = (jdata['pm2.5_aqi'] + jdata['pm2.5_aqi_b']) / 2
                        self.update_driver('AQI', round(laqi, 0))
                    elif 'pm2.5_aqi' in jdata:
                        self.update_driver('AQI', round(jdata['pm2.5_aqi'], 2))

                    LOGGER.info('AQI: {} vs. {} {}'.format(aqi, laqi, idx))
            else:
                LOGGER.error('Missing "place" field.  Is this inside or outside?')

            if 'current_temp_f' in jdata:
                self.update_driver('CLITEMP', jdata['current_temp_f'])
            if 'current_humidity' in jdata:
                self.update_driver('CLIHUM', jdata['current_humidity'])
            if 'pressure' in jdata:
                self.update_driver('BARPRES', jdata['pressure'])
            if 'current_dewpoint_f' in jdata:
                self.update_driver('DEWPT', jdata['current_dewpoint_f'])

            # do we want to collect status?
            # 2.5 10 minute average
            # 2.5 30 minute average
            # 2.5 60 minute average
            # 2.5 6 hour average
            # 2.5 24 hour average
            # 2.5 1 week average


            # age is difference between jdata[time_stamp] and sensor['last_seen']
            #  in minutes
            if 'time_stamp' in jdata and 'last_seen' in sensor:
                age = (jdata['time_stamp'] - sensor['last_seen']) / 60 
                self.update_driver('GV1', age)

        except Exception as e:
            LOGGER.error('Failed to process data: {}'.format(e))

    def query(self, cmd=None):
        self.poll('shortPoll')

    commands = {
            'QUERY': query,
            }
