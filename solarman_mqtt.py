"""            Read data with pysolarmanv5 and puplish it with mqtt                   """
"""                                                                                   """
"""                                     schwatter                                     """


from pysolarmanv5 import PySolarmanV5, V5FrameError, NoSocketAvailableError
import paho.mqtt.client as mqtt
from time import sleep


def main():

	inverter_ip_list = ["your_first_ip", "your_second_ip", "your_third_ip"] # one ore more inverters
	inverter_sn_list = [1234567890, 1234567890, 1234567890] # device serial number
	inverterport = 8899 # standardport
	mqtt_inverter_name = ["Deye1600_001", "Deye1600_002", "Deye1600_003"] # change if you want other friendly names
	mqtt_user = "your_user" # mqtt_server username
	mqtt_pw = "your_username" # mqtt_server password
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
				
				Current_power = modbus.read_holding_registers(0x56, 0x01)
				Yield_today = modbus.read_holding_registers(0x3C, 0x01)
				Total_yield = modbus.read_holding_registers(0x3F, 0x01)
				Temp = modbus.read_holding_registers(0x5A, 0x01)
				DC_Voltage_PV1 = modbus.read_holding_registers(0x6D, 0x01)
				DC_Current_PV1 = modbus.read_holding_registers(0x6E, 0x01)
				DC_Voltage_PV2 = modbus.read_holding_registers(0x6F, 0x01)
				DC_Current_PV2 = modbus.read_holding_registers(0x70, 0x01)
				DC_Voltage_PV3 = modbus.read_holding_registers(0x71, 0x01)
				DC_Current_PV3 = modbus.read_holding_registers(0x72, 0x01)
				DC_Voltage_PV4 = modbus.read_holding_registers(0x73, 0x01)
				DC_Current_PV4 = modbus.read_holding_registers(0x74, 0x01)
				
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","online",qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Current_power/", str(Current_power[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Yield_today/", str(Yield_today[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Total_yield/", str(Total_yield[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/Temp/", str(Temp[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV1/", str(DC_Voltage_PV1[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV1/", str(DC_Current_PV1[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV2/", str(DC_Voltage_PV2[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV2/", str(DC_Current_PV2[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV3/", str(DC_Voltage_PV3[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV3/", str(DC_Current_PV3[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Voltage_PV4/", str(DC_Voltage_PV4[0]),qos=1)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/DC_Current_PV4/", str(DC_Current_PV4[0]),qos=1)
				
				print("All fine, check your mqtt_client")
				sleep(1)
				clientMQTT.disconnect()
				
			except NoSocketAvailableError:
			
				clientMQTT = mqtt.Client(mqtt_inverter)
				clientMQTT.username_pw_set(mqtt_user, mqtt_pw)
				clientMQTT.connect(mqtt_srv, mqtt_port)
				clientMQTT.publish("deye/inverter/"+mqtt_inverter+"/state/","offline",qos=1)
				
				print("No socket available")
				sleep(1)
				clientMQTT.disconnect()

if __name__ == "__main__":
	main()