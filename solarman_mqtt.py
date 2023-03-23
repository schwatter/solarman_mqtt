"""    Read data with pysolarmanv5 and puplish it with mqtt    """	

__progname__    = "solarman_mqtt"
__version__     = "0.3"
__author__      = "schwatter"
__date__        = "2023-03-21"


from pysolarmanv5 import PySolarmanV5
import paho.mqtt.client as mqtt
from time import sleep
import argparse, re

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__progname__)
parser.add_argument('-apr',dest='apr_value',help='set power output (value from 1 to 100)', required=False)
args = parser.parse_args()

def main():

	inverter_ip_list = ["your_first_ip", "your_second_ip", "your_third_ip"] # one ore more inverters
	inverter_sn_list = [1234567890, 1234567890, 1234567890] # device serial number
	inverterport = 8899 # standardport
	mqtt_inverter_name = ["Deye1600_001", "Deye1600_002", "Deye1600_003"] # change if you want other friendly names
	mqtt_user = "your_user" # mqtt_server username
	mqtt_pw = "your_password" # mqtt_server password
	mqtt_srv = "your_ip" # mqtt_server ip
	mqtt_port = 1883 # mqtt_server port

	for i, (inverter_ip, inverter_sn, mqtt_inverter) in enumerate(zip(inverter_ip_list, inverter_sn_list, mqtt_inverter_name)):
		try:	
			modbus = PySolarmanV5(inverter_ip, inverter_sn, port=inverterport, mb_slave_id=0x01, verbose=False)
			clientMQTT = mqtt.Client(mqtt_inverter)
			clientMQTT.username_pw_set(mqtt_user, mqtt_pw)
			clientMQTT.connect(mqtt_srv, mqtt_port)
			
			# here you can add register
			# You can find some table here
			# https://github.com/schwatter/solarman_mqtt/blob/main/Deye_SUN600G3-230-EU_Register.xlsx
			# thx to Triple S from https://www.photovoltaikforum.com/
			
			if args.apr_value:
				if not re.match("^([1-9][0-9]?|100)$", args.apr_value):
					parser.print_help()
					quit()
	
				else:
					modbus.write_multiple_holding_registers(register_addr=40, values=[int(args.apr_value)])
					print("Change Active_Power_Regulation")
					sleep (2)
					Active_Power_Regulation = modbus.read_holding_registers(register_addr=40, quantity=1)
					sleep (1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Active_Power_Regulation/", "".join(map(str, Active_Power_Regulation)),qos=1)
					print("Active_Power_Regulation updated:", "".join(map(str, Active_Power_Regulation)), "%")
			
			else:
				
				print("Read register")
				AC_Output_Frequency = get_div_100(modbus.read_holding_registers(register_addr=79, quantity=1))
				Active_Power_Regulation = modbus.read_holding_registers(register_addr=40, quantity=1)
				Temp = get_div_100(modbus.read_holding_registers(register_addr=90, quantity=1))
				Current_power = get_div_10(modbus.read_holding_registers(register_addr=86, quantity=1))
				Yield_today = get_div_10(modbus.read_holding_registers(register_addr=60, quantity=1))
				Total_yield = get_div_10(modbus.read_holding_registers(register_addr=63, quantity=1))
				DC_all = get_div_10_all(modbus.read_holding_registers(register_addr=109, quantity=8))
				#Islanding_Protection = modbus.read_holding_registers(register_addr=46, quantity=1)

				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","online",qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Error/","------",qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Temp/", str(Temp),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Current_power/", str(Current_power),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Yield_today/", str(Yield_today),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Total_yield/", str(Total_yield),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/AC_Output_Frequency/", str(AC_Output_Frequency),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Active_Power_Regulation/", "".join(map(str, Active_Power_Regulation)),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV1/", str(DC_all[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV2/", str(DC_all[2]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV3/", str(DC_all[4]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV4/", str(DC_all[6]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV1/", str(DC_all[1]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV2/", str(DC_all[3]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV3/", str(DC_all[5]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV4/", str(DC_all[7]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Power_PV1/", str(round(DC_all[0] * DC_all[1], 1)),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Power_PV2/", str(round(DC_all[2] * DC_all[3], 1)),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Power_PV3/", str(round(DC_all[4] * DC_all[5], 1)),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Power_PV4/", str(round(DC_all[6] * DC_all[7], 1)),qos=1)
				#clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Islanding_Protection/", "".join(map(str, Islanding_Protection)),qos=1)
				
				print("All fine, check your mqtt_client")
			
			sleep(1)
			clientMQTT.disconnect()
			
		except Exception as e:
			
			clientMQTT = mqtt.Client(mqtt_inverter)
			clientMQTT.username_pw_set(mqtt_user, mqtt_pw)
			clientMQTT.connect(mqtt_srv, mqtt_port)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","offline",qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Error/", str(e),qos=1)
			
			print(e)
			sleep(1)
			clientMQTT.disconnect()

def get_div_10(divide):
	divide = int(divide[0])
	final = divide / 10
	return final
	
def get_div_10_all(divide):
	final = [x / 10 for x in divide]
	return final

def get_div_100(divide):
	divide = int(divide[0])
	final = divide / 100
	return final


if __name__ == "__main__":
	main()
