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

# MQTTメッセージを処理するコールバック関数
def on_mqtt_message(client, userdata, message):
    global frequency_register_address
    frequency_register_address = 13
    print(f"Received MQTT message: topic={message.topic}, payload={message.payload.decode()}")
    try:
        # MQTTメッセージから周波数値を取得
        frequency_value = float(message.payload.decode())
        print(f"Checking Hz...")
        modbus_client = ModbusTcpClient(config["modbus"]["host"], port=config["modbus"]["port"])
        if modbus_client.connect():
            mes = ModbusTcpClient(HOST, port=502)
            mes.connect()
            response = mes.read_holding_registers(13, 1, unit=1)
            mqtt_client.publish("haudi/hass/Nishiarai/Ecourt/frequency_status", response.registers[0]/100, qos=0, retain=True)
            modbus_client.close()
        else:
            print("Failed to connect to Modbus server.")
            time.sleep(5)
            on_mqtt_message(client,userdata,message)
            modbus_client.close()
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