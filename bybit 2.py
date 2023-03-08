import time
import datetime
import bybit
import datetime
import pandas as pd

api_key = 'PB9YOKUzzCeu4rwhpN'
secret_key = '0L35OgHGasCE9QJBoxHvoKszy40wsxAXSolG'

client = bybit.bybit(test=False, api_key=api_key, api_secret=secret_key)

def get_avg_price(ticker):
    """어제 일봉 평균가 조회"""
    interval = 'D'
    end_time = int(time.time() * 1000)
    start_time = end_time - 86400000  # 24시간 전
    df = client.Kline.Kline_get(symbol=ticker, interval=interval, from_=start_time, to=end_time, limit=2).result()
    df = pd.DataFrame(df[0]['result'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    avg_price = df.iloc[0]['close'] if df.iloc[0]['open_time'].date() == now.date() else df.iloc[1]['close']
    return avg_price




def get_current_price(ticker):
    """현재가 조회"""
    price = client.Market.Market_symbolInfo(symbol=ticker).result()[0]['result'][0]['last_price']
    return price

def get_position_size(ticker):
    """포지션 사이즈 조회"""
    pos_size = client.Positions.Positions_myPosition(symbol=ticker).result()[0]['result']
    if len(pos_size) == 0:
        return 0
    else:
        return pos_size[0]['size']

ticker = 'BTCUSD'
leverage = 10

def get_wallet_balance(currency):
    """지갑 잔고 조회"""
    wallet_balance = client.Wallet.Wallet_getBalance(coin=currency).result()
    wallet_balance = wallet_balance[0]['result']
    for balance in wallet_balance:
        if balance['coin'] == currency:
            return float(balance['wallet_balance'])
    return None

usd = get_wallet_balance('USD')

while True:
    # 어제 일봉 평균가와 현재가를 조회
    avg_price = get_avg_price(ticker)
    current_price = get_current_price(ticker)
    
    # 평균가와 현재가가 모두 조회됐을 때
    if avg_price is not None and current_price is not None:
        # 평균가 이상으로 상승하면 롱 주문
        if current_price > avg_price:
            # 기존에 숏 포지션이 있다면 청산
            short_size = get_position_size(ticker)
            if short_size < 0:
                client.Order.Order_new(side='buy', symbol=ticker, order_type='Market', qty=abs(short_size), time_in_force='GoodTillCancel', reduce_only=True, close_on_trigger=False, leverage=leverage).result()
            
            # 롱 포지션 진입
            usd = get_wallet_balance('USD')
            order_qty = round(usd * leverage / current_price / 2, 2)  # 잔고의 50%만 매수
            if usd > 10:
                client.Order.Order_new(side='buy', symbol=ticker, order_type='Market', qty=order_qty, time_in_force='GoodTillCancel', reduce_only=False, close_on_trigger=False, leverage=leverage).result()
         # 평균가 이하로 하락하면 숏 주문
        elif current_price < avg_price:
            # 기존에 롱 포지션이 있다면 청산
            long_size = get_position_size(ticker)
            if long_size > 0:
                client.Order.Order_new(side='sell', symbol=ticker, order_type='Market', qty=long_size, time_in_force='GoodTillCancel', reduce_only=True, close_on_trigger=False, leverage=leverage).result()
            
            # 숏 포지션 진입
            usd = get_wallet_balance('USD')
            order_qty = round(usd * leverage / current_price / 2, 2)  # 잔고의 50%만 매도
            if usd > 10:
                client.Order.Order_new(side='sell', symbol=ticker, order_type='Market', qty=order_qty, time_in_force='GoodTillCancel', reduce_only=False, close_on_trigger=False, leverage=leverage).result()
        
    time.sleep(10)