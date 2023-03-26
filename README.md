# solarman_mqtt

This example uses the pysolarmanv5 module to read registerdata and publish it with mqtt
It can also change the power output. See "Usage".


## Documentation

Registerlist from Triple S for Deye_SUN600G3-230-EU:<br>
https://github.com/schwatter/solarman_mqtt/blob/main/Deye_SUN600G3-230-EU_Register.xlsx

My examplescript handle three inverters at once. Change it, if you want.
Tested with Deye_SUN1600G3-230-EU.

## Usage
<pre><code>
usage: solarman_mqtt.py [-h] [-apr APR_VALUE] [-sr SINGLE_REGISTER]

options:
  -h, --help      show this help message and exit
  -apr APR_VALUE  set power output (value from 1 to 100)
  -sr SINGLE_REGISTER  read single register (value from 0 to 65535)
 
For reading only register, use no argument.
usage: python3 solarman_mqtt.py
 </code></pre>

  
## History
- 0.4 - Added Read Single Register
- 0.3 - Added Active_Power_Regulation
- 0.2 - Added MQTT
- 0.1 - Initial Setup

## Dependencies

- [jmccrohan/pysolarmanv5](https://github.com/jmccrohan/pysolarmanv5)
- [eclipse/paho.mqtt.python](https://github.com/eclipse/paho.mqtt.python)
