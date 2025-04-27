import MetaTrader5 as mt5
import time
import pandas as pd

# -------- CONFIGURATION --------
ACCOUNT = 123456789   # Your Exness MT5 account ID
PASSWORD = 'your_password'  # Your Exness password
SERVER = 'Exness-MT5Real'  # or Exness-MT5Demo
SYMBOLS = ['BTCUSD', 'XAUUSD']  # Assets to trade
LOT = 0.01  # Lot size
MAGIC = 10001  # Magic number for tracking orders

# -------- INITIALIZE --------
print("Connecting to MT5...")
mt5.initialize()
if not mt5.login(ACCOUNT, PASSWORD, server=SERVER):
    print("Login failed", mt5.last_error())
    mt5.shutdown()
    exit()
print("Connected!")

# -------- STRATEGY FUNCTION --------
def simple_strategy(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)
    if rates is None or len(rates) < 50:
        return None

    data = pd.DataFrame(rates)
    data['sma_short'] = data['close'].rolling(10).mean()
    data['sma_long'] = data['close'].rolling(50).mean()

    if data['sma_short'].iloc[-2] < data['sma_long'].iloc[-2] and data['sma_short'].iloc[-1] > data['sma_long'].iloc[-1]:
        return 'buy'
    elif data['sma_short'].iloc[-2] > data['sma_long'].iloc[-2] and data['sma_short'].iloc[-1] < data['sma_long'].iloc[-1]:
        return 'sell'
    else:
        return None

# -------- ORDER FUNCTIONS --------
def place_order(symbol, order_type):
    price = mt5.symbol_info_tick(symbol).ask if order_type == 'buy' else mt5.symbol_info_tick(symbol).bid
    type_order = mt5.ORDER_TYPE_BUY if order_type == 'buy' else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": LOT,
        "type": type_order,
        "price": price,
        "deviation": 20,
        "magic": MAGIC,
        "comment": "AutoBot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    result = mt5.order_send(request)
    print(f"{order_type.upper()} Order on {symbol}: {result}")

# -------- MAIN LOOP --------
print("Starting auto-trading bot...")
while True:
    for symbol in SYMBOLS:
        decision = simple_strategy(symbol)
        if decision:
            place_order(symbol, decision)
    time.sleep(300)  # Wait 5 minutes before checking again

# -------- SHUTDOWN (if needed) --------
# mt5.shutdown()
