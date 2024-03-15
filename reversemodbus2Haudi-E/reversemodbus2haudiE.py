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
def set_inverter_reversemode(client, register_address, frequency):
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

#インバータの運転状態チェックして止まってたら動かす
def check_running_status_and_run(client):
    response = client.read_holding_registers(8, 1, unit=1)
    if not response.isError():
        print(f"running status is: {response.registers[0]}")

    # if invert is stop (status = 502), write register 40009 and run 
    if(response.registers[0] == 512):
        response = client.write_register(8, 4, unit=1)  

        # 応答の確認
        if not response.isError():
            print("Write operation successful.")
        else:
            print("Error writing register:", response)

# MQTTメッセージを処理するコールバック関数
def on_mqtt_message(client, userdata, message):
    global reversemode_register_address
    reversemode_register_address = 8
    print(f"Received MQTT message: topic={message.topic}, payload={message.payload.decode()}")
    try:
        # MQTTメッセージから周波数値を取得
        reverse_mode = round(float(message.payload.decode()),1)
        modbus_client = ModbusTcpClient(config["modbus"]["host"], port=config["modbus"]["port"])
        if modbus_client.connect():
            if reverse_mode == 1:
                check_running_status_and_run(modbus_client)
                response = modbus_client.write_register(8, 4, unit=1)
                modbus_client.close()
            elif reverse_mode == 0:
                check_running_status_and_run(modbus_client)
                response = modbus_client.write_register(8, 2, unit=1)
                modbus_client.close()
        else:
            print("Failed to connect to Modbus server.")
            time.sleep(1)
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
