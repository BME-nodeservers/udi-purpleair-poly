The PurpleAir Plug-in supports both local sensor access and remote sensor access.

To access the local sensor data you need to know the IP address of the sensor. Then simply
configure a custom parameter with the sensor name and the IP address.

To access public sensor data from PurpleAir, you need a READ API KEY. You will need to have
an account on the PurpleAir website.  From there you can manage your API keys.  

The PurpleAir plug-in uses the short poll time to query for sensor data.  PurpleAir has
requested that API queries be limited to once per 10 minutes (short poll time of 600). However
if you are configured for local sensor data, you may use any short poll time.

The PurpleAir node server must be told which PurpleAir sensor devices it should monitor.  To
do that you need to enter Custom Parameters describing each device.

In the 'key' field put the name you want to use to identify the Purple Air device.  Don't use
special characters and keep it under 14 characters long.

In the 'value' field put either the sensor ID or the IP address of the Purple Air device. 

Examples:

MyHome:  345678
Outside: 192.168.1.34

You can get the sensor ID number from the PurpleAir public sensor map at https://map.purpleair.com.
Click on the sensor you want to monitor and hover over the "Get This Widget" link.  Look for
something like "PurpleAirWidget_nnnnnn_module.  The sensor id is the "nnnnnn" number.

