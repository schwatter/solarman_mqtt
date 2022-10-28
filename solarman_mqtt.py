"""            Read data with pysolarmanv5 and puplish it with mqtt                   """
"""                                                                                   """
"""                                     schwatter                                     """


from pysolarmanv5 import PySolarmanV5
import paho.mqtt.client as mqtt
from time import sleep


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
			# https://onedrive.live.com/view.aspx?resid=16A457D539B343A2!3421&ithint=file%2cxlsx&authkey=!ACea2L7tVWRMVaw
			# thx to Triple S from https://www.photovoltaikforum.com/
			
			Temp = get_div_100(modbus.read_holding_registers(0x5A, 0x01))
			Current_Power = get_div_10(modbus.read_holding_registers(0x56, 0x01))
			Yield_Today = get_div_10(modbus.read_holding_registers(0x3C, 0x01))
			Total_Yield = get_div_10(modbus.read_holding_registers(0x3F, 0x01))
			DC_All = get_div_10_all(modbus.read_holding_registers(0x6D, 0x08))
			
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","online",qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Error/","------",qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Temp/", str(Temp),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Current_Power/", str(Current_Power),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Yield_Today/", str(Yield_Today),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Total_Yield/", str(Total_Yield),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV1/", str(DC_All[0]),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV2/", str(DC_All[1]),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV3/", str(DC_All[2]),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV4/", str(DC_All[3]),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV1/", str(DC_All[4]),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV2/", str(DC_All[5]),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV3/", str(DC_All[6]),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV4/", str(DC_All[7]),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Power_PV1/", str(round(DC_All[0] * DC_All[1], 1)),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Power_PV2/", str(round(DC_All[2] * DC_All[3], 1)),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Power_PV3/", str(round(DC_All[4] * DC_All[5], 1)),qos=1)
			clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Power_PV4/", str(round(DC_All[6] * DC_All[7], 1)),qos=1)
			
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
