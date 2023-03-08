### bybit long open ###
resp = session.place_active_order(
    symbol="BTCUSDT",
    side="Buy",
    order_type="Market",
    qty=0.001,
    time_in_force="GoodTillCancel",
    reduce_only=False,
    close_on_trigger=False
)