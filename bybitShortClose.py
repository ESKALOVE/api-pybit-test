from pybit.usdt_perpetual import HTTP
import numpy as np
import os.path
import time
from IPython.display import clear_output
#### 바이비트 키
with open("bybit2.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    api_secret = lines[1].strip()
session = HTTP(
    endpoint="https://api.bybit.com", 
    api_key=api_key, 
    api_secret=api_secret
)
#### 소수점 N자리까지만 표시 함수 ###
def truncate(num, n):
    integer = int(num * (10**n))/(10**n)
    return float(integer)
### 기본 세팅 ###
USDT = session.get_wallet_balance(
    coin="USDT")['result']['USDT']['available_balance']  # USDT 보유량
position_size = session.my_position(symbol='BTCUSDT')['result'][1]['size'] # BTCUSDT short 구매량
position_size_long = session.my_position(symbol='BTCUSDT')['result'][0]['size'] # BTCUSDT long 구매량
position_average = session.my_position(symbol='BTCUSDT')[
    'result'][1]['entry_price'] # BTCUSDT Short average position price
position_average_long = session.my_position(symbol='BTCUSDT')[
    'result'][0]['entry_price'] # BTCUSDT long average position price
position_leverage = session.my_position(symbol='BTCUSDT')[
    'result'][1]['leverage'] # BTCUSDT Short 레버리지
position_leverage_long = session.my_position(symbol='BTCUSDT')[
    'result'][0]['leverage'] # BTCUSDT long 레버리지
BTCUSDT_now = float(session.latest_information_for_symbol(
    symbol='BTCUSDT')['result'][0]['last_price'])  # BTCUSDT 현재가격
min_price = BTCUSDT_now
max_price = BTCUSDT_now
if position_size == 0:
    trade_state_bybit = 1 # 매도상태
else:
    trade_state_bybit = 0 # short open 상태
if position_size_long != 0:
    trade_state_bybit = 2 # long open 상태
#### 출력하기 ###
print(USDT, position_size, position_size_long, BTCUSDT_now, trade_state_bybit)
if os.path.isfile('min_max_save.npy'):
    min_price, max_price = np.load('min_max_save.npy')  # 멈추기 전 min, max 값받아오기
### bybit short close ###
position_size_long = session.my_position(symbol='BTCUSDT')['result'][1]['size'] # BTCUSDT short 구매량
resp = session.place_active_order(
    symbol="BTCUSDT",
    side="Buy",
    order_type="Market",
    qty=float(position_size),
    time_in_force="GoodTillCancel",
    reduce_only=False,
    close_on_trigger=False
)