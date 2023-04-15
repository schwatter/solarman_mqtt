"""    Read data with pysolarmanv5 and puplish it with mqtt    """	

__progname__    = "solarman_mqtt"
__version__     = "0.6"
__author__      = "schwatter"
__date__        = "2023-04-15"


from pysolarmanv5 import PySolarmanV5
import paho.mqtt.client as mqtt
from datetime import datetime
from time import sleep
import argparse, re

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__progname__)
parser.add_argument('-apr',dest='apr_value',help='write power output (value from 1 to 100)', required=False)
parser.add_argument('-dt',action='store_true',help='write date and time (reg 22,23,24)', required=False)
parser.add_argument('-mqtt',action='store_true',help='all actions pushed to mqtt client', required=False)
parser.add_argument('-rsr',dest='rs_register',help='read single register (value from 0 to 65535)', required=False)
parser.add_argument('-wsr',dest='ws_register',nargs=2,metavar=('Register', 'Value'),type=int,default=[],help='write single register (40 100) Caution !!!', required=False)
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
			modbus = PySolarmanV5(inverter_ip, inverter_sn, port=inverterport, mb_slave_id=1, verbose=False)
			clientMQTT = mqtt.Client(mqtt_inverter)
			clientMQTT.username_pw_set(mqtt_user, mqtt_pw)
			if args.apr_value:
				if not re.match("^([1-9][0-9]?|100)$", args.apr_value):
					parser.print_help()
					quit()
				else:
					print("Change Active_Power_Regulation")
					modbus.write_multiple_holding_registers(register_addr=40, values=[int(args.apr_value)])
					sleep (2)
					Active_Power_Regulation = modbus.read_holding_registers(register_addr=40, quantity=1)
					if args.mqtt:
						clientMQTT.connect(mqtt_srv, mqtt_port)
						clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","online",qos=1)
						clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Error/","------",qos=1)
						clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Active_Power_Regulation/", "".join(map(str, Active_Power_Regulation)),qos=1)
						clientMQTT.disconnect()
					else:
						print("Active_Power_Regulation updated:", "".join(map(str, Active_Power_Regulation)), "%")	
			elif args.dt:
				print("Set time")
				now = datetime.now()
				ym = 256 * (now.year % 100) + now.month
				modbus.write_multiple_holding_registers(register_addr=22, values=[int(ym)])
				dh = 256 * now.day + now.hour
				modbus.write_multiple_holding_registers(register_addr=23, values=[int(dh)])
				ms = 256 * now.minute + now.second
				modbus.write_multiple_holding_registers(register_addr=24, values=[int(ms)])
				if args.mqtt:
					clientMQTT.connect(mqtt_srv, mqtt_port)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","online",qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Error/","------",qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Actual_DateTime/", "22=" + str(ym) + "/23="+ str(dh) + "/24=" + str(ms),qos=1)
					clientMQTT.disconnect()
				else:
					print("Time updated")
			elif args.rs_register:
				if not re.match("^(?:0|[1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$", args.rs_register):
					parser.print_help()
					quit()
				else:
					print("Read single register")
					sr = modbus.read_holding_registers(register_addr=int(args.rs_register), quantity=1)
					if args.mqtt:
						clientMQTT.connect(mqtt_srv, mqtt_port)
						clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","online",qos=1)
						clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Error/","------",qos=1)
						clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Read_Single_Register/", args.rs_register+ "/" + "".join(map(str, sr)),qos=1)
						clientMQTT.disconnect()
					else:
						print("Single register: " + args.rs_register + " Value:", "".join(map(str, sr)))
						print("finished")
			elif args.ws_register:
				print("Write single register")
				wsr = args.ws_register
				modbus.write_multiple_holding_registers(register_addr=wsr[0], values=[wsr[1]])
				if args.mqtt:
						clientMQTT.connect(mqtt_srv, mqtt_port)
						clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","online",qos=1)
						clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Error/","------",qos=1)
						clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Write_Single_Register/", str(wsr[0]) + "=" + str(wsr[1]),qos=1)
						clientMQTT.disconnect()
				else:
					print("Single register:", wsr[0], "value:", wsr[1])
					print("finished")
			else:
				# here you can add or change register
				# some table, thx to Triple S from https://www.photovoltaikforum.com/
				# https://github.com/schwatter/solarman_mqtt/blob/main/Deye_SUN600G3-230-EU_Register.xlsx
				
				print("Read register")
				AC_Output_Frequency = get_div_100(modbus.read_holding_registers(register_addr=79, quantity=1))
				Active_Power_Regulation = modbus.read_holding_registers(register_addr=40, quantity=1)
				Islanding_Protection = modbus.read_holding_registers(register_addr=46, quantity=1)
				Temp = get_div_100(modbus.read_holding_registers(register_addr=90, quantity=1))
				Current_power = get_div_10(modbus.read_holding_registers(register_addr=86, quantity=1))
				Yield_today = get_div_10(modbus.read_holding_registers(register_addr=60, quantity=1))
				Total_yield = get_div_10(modbus.read_holding_registers(register_addr=63, quantity=1))
				DC_all = get_div_10_all(modbus.read_holding_registers(register_addr=109, quantity=8))
				if args.mqtt:
					clientMQTT.connect(mqtt_srv, mqtt_port)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","online",qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Error/","------",qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Temp/", str(Temp),qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Current_power/", str(Current_power),qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Yield_today/", str(Yield_today),qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Total_yield/", str(Total_yield),qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/AC_Output_Frequency/", str(AC_Output_Frequency),qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Active_Power_Regulation/", "".join(map(str, Active_Power_Regulation)),qos=1)
					clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Islanding_Protection/", "".join(map(str, Islanding_Protection)),qos=1)
					clientMQTT.disconnect()
					clientMQTT.connect(mqtt_srv, mqtt_port)
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
					clientMQTT.disconnect()
					print("All fine, check your mqtt_client")
				else:
					print("Inverter: ", str(mqtt_inverter))
					print("Temp: ", str(Temp))
					print("Current_power: ", str(Current_power))
					print("Yield_today: ", str(Yield_today))
					print("Total_yield: ", str(Total_yield))
					print("AC_Output_Frequency: ", str(AC_Output_Frequency))
					print("Active_Power_Regulation: ", "".join(map(str, Active_Power_Regulation)))
					print("Islanding_Protection: ", "".join(map(str, Islanding_Protection)))
					print("DC_Voltage_PV1: ", str(DC_all[0]))
					print("DC_Voltage_PV2: ", str(DC_all[2]))
					print("DC_Voltage_PV3: ", str(DC_all[4]))
					print("DC_Voltage_PV4: ", str(DC_all[6]))
					print("DC_Current_PV1: ", str(DC_all[1]))
					print("DC_Current_PV2: ", str(DC_all[3]))
					print("DC_Current_PV3: ", str(DC_all[5]))
					print("DC_Current_PV4: ", str(DC_all[7]))
					print("DC_Power_PV1: ", str(round(DC_all[0] * DC_all[1], 1)))
					print("DC_Power_PV2: ", str(round(DC_all[2] * DC_all[3], 1)))
					print("DC_Power_PV3: ", str(round(DC_all[4] * DC_all[5], 1)))
					print("DC_Power_PV4: ", str(round(DC_all[6] * DC_all[7], 1)))
					print("------------------------------")
			
		except Exception as e:
			if args.mqtt:			
				clientMQTT = mqtt.Client(mqtt_inverter)
				clientMQTT.username_pw_set(mqtt_user, mqtt_pw)
				clientMQTT.connect(mqtt_srv, mqtt_port)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","offline",qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Error/", str(e),qos=1)
				sleep(1)
				clientMQTT.disconnect()
			else:
				print(e)

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
