from pymodbus.client.tcp import ModbusTcpClient

# 接続設定
HOST = '192.168.85.201'
PORT = 502

# Modbusインスタンスを作成
client = ModbusTcpClient(HOST, port=PORT)

# 接続を開始
client.connect()

# 単一のレジスタを読み取り
address = 8

print(f"About {HOST} resister 40010 runnning status...")
# 結果を表示
response = client.read_holding_registers(address, 1, unit=1)
if not response.isError():
    print(f"running status is: {response.registers[0]}")
    
if(response.registers[0] == 512):
    response = client.write_register(8, 4, unit=1)  # 第一引数に第二引数の値を書き込む関数、unitはそのままでよい

    # 応答の確認
    if not response.isError():
        print("Write operation successful.")
    else:
        print("Error writing register:", response)

# 接続を閉じる
client.close()
