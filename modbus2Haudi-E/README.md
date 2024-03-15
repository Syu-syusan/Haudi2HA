# modbus2Haudi
FR-E820-1.5KEPAのインバータをMQTT経由でMosbus/TCP通信することで、周波数の制御をするプログラム。

# how to use
mosquittoのインストールが必須。インストール後、config.ymlにIPアドレスを設定し、以下を実行。

```
pip3 install -r requirements.txt
python3 modbus2haudi.py
```