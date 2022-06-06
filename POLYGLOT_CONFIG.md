To access public sensor data from PurpleAir, you need a READ API KEY. Currently the only
way to get a key is to email contact@purpleair.com and request one.

You do not need to own a PurpleAir sensor to get an API key, but you will need to provide your
first and last name when you request one. When you get the key, add it to the APIKey custom 
parameter.

The PurpleAir node server uses the short poll time to query for sensor data.  PurpleAir has
requested that queries be limited to once per 10 minutes (short poll time of 600).

The PurpleAir node server must be told which PurpleAir sensor devices it should monitor.

To do that you need to enter Custom Parameters describing each device.

In the 'key' field put the name you want to use to identify the Purple Air device.  Don't use
special characters and keep it under 14 characters long.

In the 'value' field put the sensor ID of the Purple Air device. This is typically just a number.

Example:

MyHome:  345678

You can get the sensor ID number from the PurpleAir public sensor map at https://map.purpleair.com.
Click on the sensor you want to monitor and hover over the "Get This Widget" link.  Look for
something like "PurpleAirWidget_nnnnnn_module.  The sensor id is the "nnnnnn" number.

