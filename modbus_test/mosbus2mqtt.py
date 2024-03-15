from pymodbus.client.tcp import ModbusTcpClient

# 接続設定
HOST = '192.168.85.201'
PORT = 502

# Modbusインスタンスを作成
client = ModbusTcpClient(HOST, port=PORT)

# 接続を開始
client.connect()

address = 0
ADDRESS_START = 0
ADDRESS_END = 20

# 結果を表示
for address in range(ADDRESS_START, ADDRESS_END):
    response = client.read_holding_registers(address, 1, unit=1)
    #if not response.isError():
        #print(f"Current {address+40001} Value: {response.registers[0]}")

invert_situationplus = 7 # インバータ状態/制御入力命令(拡張)
invert_situation = 8 # インバータ状態/制御入力命令
run_mode = 9 # 運転モード/インバータ設定
run_frequency = 13 # 運転周波数
value = 2
response = client.write_register(8, 4, unit=1)  # 第一引数に第二引数の値を書き込む関数、unitはそのままでよい

# 応答の確認
if not response.isError():
    print("Write operation successful.")
else:
    print("Error writing register:", response)

for address in range(ADDRESS_START, ADDRESS_END):
    response = client.read_holding_registers(address, 1, unit=1)
    if not response.isError():
        print(f"Current {address+40001} Value: {response.registers[0]}")
