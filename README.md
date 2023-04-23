# solarman_mqtt

This example uses the pysolarmanv5 module to read and write registerdata.<br>
The hardcoded registers are for Deye Microinverters like:<br>
SUN 300/500/600/800/1000/1300/1600/2000<br>

See "Usage"


## Documentation

Registerlist from Triple S for Deye_SUN600G3-230-EU:<br>
https://github.com/schwatter/solarman_mqtt/blob/main/Deye_SUN600G3-230-EU_Register.xlsx

My examplescript handle three inverters at once. Change it, if you want.
Tested with Deye_SUN1600G3-230-EU.

## Usage

Setup your inverter details.
<pre><code>
inverter_ip_list = ["your_first_ip", "your_second_ip", "your_third_ip"] # one ore more inverters
inverter_sn_list = [1234567890, 1234567890, 1234567890] # device serial number
inverterport = 8899 # standardport
mqtt_inverter_name = ["Deye1600_001", "Deye1600_002", "Deye1600_003"] # change if you want other friendly names
mqtt_user = "your_user" # mqtt_server username
mqtt_pw = "your_password" # mqtt_server password
mqtt_srv = "your_ip" # mqtt_server ip
mqtt_port = 1883 # mqtt_server port
 </code></pre>
 
 User options
<pre><code>
usage: solarman_mqtt.py [-h] [-apr APR_VALUE] [-dt] [-mqtt] [-rsr RS_REGISTER] [-wsr Register Value]

solarman_mqtt

options:
  -h, --help           show this help message and exit
  -apr APR_VALUE       write power output (value from 1 to 100)
  -dt                  write date and time (reg 22,23,24)
  -mqtt                all actions pushed to mqtt client
  -rsr RS_REGISTER     read single register (value from 0 to 65535)
  -wsr Register Value  write single register (40 100) Caution !!!
 
For reading only register, use no argument.
usage: python3 solarman_mqtt.py

For reading only register and push all to mqtt.
usage: python3 solarman_mqtt.py -mqtt

So in sum, "-mqtt" can be combined with all flags and all output lands in the mqtt_client.
If not set, all output lands on the local console.
 </code></pre>

  
## History
- 0.8 - Added Running_Status
- 0.7 - Added every5min loop with ping to -dt. Best start script @sunrise.
- 0.6 - Changed MQTT as optional
- 0.5 - Added Write Single Register and Write Actual Time
- 0.4 - Added Read Single Register
- 0.3 - Added Active_Power_Regulation
- 0.2 - Added MQTT
- 0.1 - Initial Setup

## Dependencies

- [jmccrohan/pysolarmanv5](https://github.com/jmccrohan/pysolarmanv5)
- [eclipse/paho.mqtt.python](https://github.com/eclipse/paho.mqtt.python)
