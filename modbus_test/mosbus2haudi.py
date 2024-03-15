from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
import paho.mqtt.client as mqtt
from pymodbus.exceptions import ModbusException
import yaml
import logging

# 設定ファイルの読み込み
with open("config.yml", "r") as yml:
    config = yaml.safe_load(yml)
HOST = str(config["modbus"]["host"])
# インバータの周波数を設定する関数
def set_inverter_frequency(client, register_address, frequency):
    frequency = int(frequency * 100)
    try:
        # レジスタへの書き込みを試みる
        response = client.write_registers(register_address, frequency, unit=1)
        if not response.isError():
            print("Write operation successful.")
            print(f"About {HOST} resister...")
            response = client.read_holding_registers(register_address, 1, unit=1)
            print(f"Resister {register_address+40001} Value: {response.registers[0]}")
        else:
            print("Error writing register:", response)
    except ModbusException as e:
        print(f"Failed to set inverter frequency: {e}")

# MQTTメッセージを処理するコールバック関数
def on_mqtt_message(client, userdata, message):
    global frequency_register_address
    frequency_register_address = 13
    print(f"Received MQTT message: topic={message.topic}, payload={message.payload.decode()}")
    try:
        # MQTTメッセージから周波数値を取得
        frequency_value = float(message.payload.decode())
        print(f"Setting inverter frequency to {frequency_value} Hz...")
        modbus_client = ModbusTcpClient(config["modbus"]["host"], port=config["modbus"]["port"])
        if modbus_client.connect():
            set_inverter_frequency(modbus_client,  frequency_register_address, frequency_value)
            modbus_client.close()
        else:
            print("Failed to connect to Modbus server.")
    except ValueError as e:
        print(f"Error processing MQTT message: {e}")

# MQTTクライアントの設定
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code " + str(rc))
    client.subscribe(config["mqtt"]["frequency_topic"])

def start_mqtt_client():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_mqtt_message
    mqtt_client.connect(config["mqtt"]["host"], config["mqtt"]["port"], 10)
    mqtt_client.loop_forever()

if __name__ == "__main__":
    start_mqtt_client()