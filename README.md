
# PurpleAir 

This is a plug-in to access AQI data from the PurpleAir air monitoring sensors.  

The plug-in can be configured to get the data from a sensor on your local network or
it can query the PurpleAir cloud servers.

To access data from the PurpleAir cloud severs you need to create an account to
get a READ API key.  See https://develop.purpleair.com/.  

Local data queries and cloud data queries return slightly different data.  From the 
cloud we are able to get data averaged over various lengths of time.  For example
we have access to the PM 2.5 value averaged over 24 hours. The local queries will only
return the current PM 2.5 value.  The plug-in will create nodes with a different template
for local and cloud configurations. 

Another difference between local and cloud queries is in how often we check for new data.
When querying data from the cloud, PurpleAir has requested that queries be limited to once
every 10 minutes.  Local queries can be made as often as 1 every second although this may
lead to high CPU usage on the Polisy/eisy so using 10 or more seconds is recommended.

You could configure the plug-in to get both the local and cloud based data but because of
the time/averaging you may get different values returned for the same fields.


### Controller node
 * sys.node.[address].ST      (Node sever online)

### Local Air Quality node
 * sys.node.[address].CLITEMP (current temperature)
 * sys.node.[address].CLIHUM  (current humidity)
 * sys.node.[address].BARPRES (current barometric pressure)
 * sys.node.[address].DEWPT   (current dewponit)
 * sys.node.[address].PM25    (current PM 2.5 value)
 * sys.node.[address].PM10    (current PM 1.0 value)
 * sys.node.[address].GV0     (current PM 10 value)
 * sys.node.[address].AQI     (EPA Air Quality Index number)
 * sys.node.[address].GV11    (EPA Air Quality Index category)
 * sys.node.[address].GV12    (Data confidence)

### Cloud Air Quality node
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
1. Polyglot PG3 or PG3x
2. ISY firmware 5.7.x or later
