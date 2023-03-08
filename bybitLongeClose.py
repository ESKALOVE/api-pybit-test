### bybit long close ###
position_size_long = session.my_position(symbol='BTCUSDT')['result'][0]['size'] # BTCUSDT long 구매량
resp = session.place_active_order(
    symbol="BTCUSDT",
    side="Sell"
    order_type="Market",
    qty=float(position_size_long),
    time_in_force="GoodTillCancel",
    reduce_only=False,
    close_on_trigger=False
)