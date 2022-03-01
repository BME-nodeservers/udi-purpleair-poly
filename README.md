
# Purple Air 

This is a node server to pull AQI data from the Purple Air network and make it
available to a [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY)
[Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with 
Polyglot V3 running on a [Polisy](https://www.universal-devices.com/product/polisy/)

(c) 2020,2021 Robert Paauwe

## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. From the Polyglot dashboard, select the Purple Air node server and configure (see configuration options below).
4. Once configured, the Purple Air node server should update the ISY with the proper nodes and begin filling in the node data.
5. Restart the Admin Console so that it can properly display the new node server nodes.

### Node Settings
The settings for this node are:

#### Short Poll
   * How often to poll the Purple Air service for current AQI data (in seconds)
#### Long Poll
   * Not used
#### Custom Parameters
	* A list of Purple Air devices to monitor. For the 'key', enter a name to use to identify the device (under 14 characters, no special characters). For the 'value' enter the Purple Air sensor ID. This is typically just a number.

## Node substitution variables
### Controller node
 * sys.node.[address].ST      (Node sever online)

### Air Quality node
 * sys.node.[address].CLITEMP (current temperature)
 * sys.node.[address].CLIHUM  (current humidity)
 * sys.node.[address].BARPRES (current barometric pressure)
 * sys.node.[address].GV0     (current PM2.5 value speed)
 * sys.node.[address].GV1     (Age of data in minutes)
 * sys.node.[address].GV3     (10 minute average)
 * sys.node.[address].GV4     (30 minute average)
 * sys.node.[address].GV5     (60 minute average)
 * sys.node.[address].GV6     (6 hour average)
 * sys.node.[address].GV7     (24 hour average)
 * sys.node.[address].GV8     (1 week average)
 * sys.node.[address].GV10    (EPA Air Quality Index number)
 * sys.node.[address].GV11    (EPA Air Quality Index category)
 * sys.node.[address].GV12    (Data confidence)


## Requirements
1. Polyglot V3.
2. ISY firmware 5.3.x or later

# Release Notes

- 2.0.1 03/01/2022
   - fix query for main node.
- 2.0.0 03/01/2021
   - Updated to run on Polyglot Version 3
- 1.0.4 08/31/2020
   - Fix confidence level calculation
- 1.0.3 08/31/2020
   - Remove test message
   - Trap and report connection errors
- 1.0.2 08/29/2020
   - Change to allow multiple Purple air device nodes.
- 1.0.1 08/29/2020
   - Add data confidence 
   - Fix typo
- 1.0.0 08/27/2020
   - Initial version.
