from pymodbus.client.tcp import ModbusTcpClient

# 接続設定
HOST = '192.168.85.202'
PORT = 502

# Modbusインスタンスを作成
client = ModbusTcpClient(HOST, port=PORT)

# 接続を開始
client.connect()

# 単一のレジスタを読み取り
address = 0
ADDRESS_START = 0
ADDRESS_END = 20

print(f"About {HOST} resister...")
# 結果を表示
for address in range(ADDRESS_START, ADDRESS_END):
    response = client.read_holding_registers(address, 1, unit=1)
    if not response.isError():
        print(f"Resister {address+40001} Value: {response.registers[0]}")

# 接続を閉じる
client.close()
