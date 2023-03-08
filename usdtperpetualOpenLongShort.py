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

loop_count = 0
error_count = 0
#### 무한루프  ####
while True:
    try:
        loop_count += 1
        BTCUSDT_now = float(session.latest_information_for_symbol(
            symbol='BTCUSDT')['result'][0]['last_price'])  # BTCUSDT 현재가격
        if BTCUSDT_now < min_price:
            min_price= BTCUSDT_now   # 최저가를 갱신
        if BTCUSDT_now > max_price:
            max_price= BTCUSDT_now   # 최고가를 갱신
        if BTCUSDT_now > min_price*1.01: # 현재가격이 최저가의 +1% 이상일때,
            if trade_state_bybit == 0:   # 숏 오픈일때, 숏 클로즈 하기
                position_size = session.my_position(symbol='BTCUSDT')['result'][1]['size']  # Short 구매량
                if position_size >= 0.001:
                    resp = session.place_active_order(
                        symbol="BTCUSDT",
                        side="Buy",
                        order_type="Market",
                        qty=float(position_size),      # short close 보유량 전체를
                        time_in_force="GoodTillCancel",
                        reduce_only=True,
                        Close_on_trigger=False
                    )                           # 바이비트 숏 클로즈
                    trade_state_bybit = 1                   # long & short close 상태표시
            if trade_state_bybit == 1:               # long & short close 일 때 long open하기
                position_size_long = session.my_position(symbol='BTCUSDT')['result'][0]['size']  # long 구매량
                if position_size_long == 0:
                    USDT = session.get_wallet_balance(
                        coin="USDT")['result']['USDT']['available_balance']  # USDT 보유량
                    available_BTCUSDT = USDT/BTCUSDT_now            # 매수가능한 BTCUSDT 수량
                    if available_BTCUSDT >= 0.001:
                        resp = session.place_active_order(
                        symbol="BTCUSDT",
                        side="Buy",
                        order_type="Market",
                        qty=0.001,         # Long open size 0.001 BTCUSDT open
                        time_in_force="GoodTillCancel",
                        reduce_only=True,
                        Close_on_trigger=False
                    )                               # bybit long open
                    trade_state_bybit = 2           # long open 상태
                    min_price = BTCUSDT_now         # long open 이후 min 값 재설정
                    max_price = BTCUSDT_now         # long open 이후 max 값 재설정
                    time.sleep(1)
                    position_size_long = session.my_position(symbol='BTCUSDT')[
                        'result'][0]['size']  # long 구매량
                    position_average_long = session.my_position(symbol='BTCUSDT')[
                        'result'][0]['entry_price']  # BTCUSDT long 구매 가격
                    position_leverage_long = session.my_position(symbol='BTCUSDT')[
                        'result'][0]['leverage']  # BTCUSDT long 레버리지 확인

        if BTCUSDT_now < max_price*0.99: # 현재가격이 최고가의 -1% 이하일때,
            if trade_state_bybit == 2:   # 롱 오픈일때, 롱 클로즈 하기
                position_size_long = session.my_position(symbol='BTCUSDT')['result'][0]['size']  # long 구매량
                if position_size_long >= 0.001:
                    resp = session.place_active_order(
                        symbol="BTCUSDT",
                        side="Sell",
                        order_type="Market",
                        qty=float(position_size_long),      # long close 보유량 전체를
                        time_in_force="GoodTillCancel",
                        reduce_only=True,
                        Close_on_trigger=False
                    )                           # 바이비트 long 클로즈
                    trade_state_bybit = 1                   # long & short close 상태표시
            if trade_state_bybit == 1:               # long & short close 일 때 short open하기
                position_size = session.my_position(symbol='BTCUSDT')['result'][1]['size']  # short 구매량
                if position_size_long == 0:
                    USDT = session.get_wallet_balance(
                        coin="USDT")['result']['USDT']['available_balance']  # USDT 보유량
                    available_BTCUSDT = USDT/BTCUSDT_now            # 매수가능한 BTCUSDT 수량
                    if available_BTCUSDT >= 0.001:
                        resp = session.place_active_order(
                            symbol="BTCUSDT",
                            side="Sell",
                            order_type="Market",
                            qty=0.001,         # Short open size 0.001 BTCUSDT open
                            time_in_force="GoodTillCancel",
                            reduce_only=True,
                            Close_on_trigger=False
                        )                               # bybit short open
                        trade_state_bybit = 0           # short open 상태
                        min_price = BTCUSDT_now         # short open 이후 min 값 재설정
                        max_price = BTCUSDT_now         # short open 이후 max 값 재설정
                        time.sleep(1)
                        position_size_long = session.my_position(symbol='BTCUSDT')[
                            'result'][1]['size']        # short 구매량
                        position_average_long = session.my_position(symbol='BTCUSDT')[
                            'result'][1]['entry_price']  # BTCUSDT short 구매 가격
                        position_leverage_long = session.my_position(symbol='BTCUSDT')[
                            'result'][1]['leverage']  # BTCUSDT long 레버리지 확인                          
        np.save('min_max_save.npy', [min_price, max_price])

        if trade_state_bybit == 1:
            print('(close 상태)', position_size, ' / (손익)',
                  '0 %', '/ (min max now)', min_price, max_price, BTCUSDT_now)
        if trade_state_bybit == 0:
            print('(short open 상태/레버리지)', position_size, position_leverage, ' / (손익)',
                  round((position_average-BTCUSDT_now)/position_average*100, 3), '%',
                  ' / (min max now)',  min_price, max_price, BTCUSDT_now)
        if trade_state_bybit == 2:
            print('(long open 상태/레버리지)', position_size_long, position_leverage_long, ' / (손익)',
                  round((BTCUSDT_now-position_average_long)/position_average_long*100, 3), '%',
                  ' / (min max now)',  min_price, max_price, BTCUSDT_now)
        np.save('min_max_save.npy', [min_price, max_price])
        time.sleep(10)          # 10초간 멈춤
        if loop_count % 10 == 0:
           clear_output(wait=True)
               #10초*10번  = 100초 마다 print 결과 삭제
    
    except Exception as e:
        print(e)

        error_count +=1
        if error_count > 5:
            raise e 
        break
        print(error_count)
    pass

                    