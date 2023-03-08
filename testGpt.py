import bybit
import numpy as np


api_key = 'PB9YOKUzzCeu4rwhpN'
secret_key = '0L35OgHGasCE9QJBoxHvoKszy40wsxAXSolG'

# API 키 및 시크릿 키 설정
client = bybit.bybit(test=False, api_key='api_key', api_secret='api_secret')

# 거래 정보 입력
symbol = 'BTCUSD'
side = 'Buy'
order_type = 'Limit'
leverage = 10 # 레버리지는 10배로 가정

# 가격 정보 조회
#klines = client.Kline.Kline_get(symbol=symbol, interval='1', limit=50).result()[0]['result']
#close_prices = np.array([float(k['close']) for k in klines])

# 변동성 돌파 전략 계산
#average_true_range = np.mean(np.abs(np.diff(close_prices)))
#breakout_price = close_prices[-1] + average_true_range

# 잔고 조회
#balance = client.Wallet.Wallet_getBalance(coin='USDT').result()[0]['result'][0]
#available_balance = balance['available_balance']

# 최대 매수 가능 수량 계산
symbol_info = client.Symbol.Symbol_get(symbol=symbol).result()[0]['result'][0]
max_order_qty = available_balance * breakout_price * leverage / symbol_info['tick_size'] // leverage / symbol_info['lot_size']

# 매수 주문 실행
order_result = client.Order.Order_new(
    symbol=symbol,
    side=side,
    order_type=order_type,
    qty=max_order_qty,
    price=breakout_price,
    time_in_force='GoodTillCancel'
).result()

print(order_result)
