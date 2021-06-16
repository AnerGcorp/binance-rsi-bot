import websocket
import pprint
import json
import talib
import numpy

from binance import Client
from binance.enums import *

SOCKET =  "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL="ETHUSDT"
TRADE_QUANTITY = 0.05

closes = []
in_position = False

api_key = "H603dodxSRADU7gTY423YEsoAzqm9RtTS2I3JWerbnO5xAFuexUAddRcv3PLvffb"
api_secret = "hBeVPtjKTBLS4pj6EungCyhtdaJzx0Tiz5Pz6nE2LvvP5L8sx85qF3aDDxh84DvC"

client = Client(api_key, api_secret, tld="us")

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("Sending order..")
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantity)
        return True
    except Exception as e:
        return False

def on_open(ws):
  print("Opened Connection")

def on_close(ws, code, msg):
  print(f"Closed Connection {code}: {msg}")

def on_message(ws, message):
  global closes

  print("Received Message")
  json_message = json.loads(message)

  candle = json_message['k']
  is_candle_closed = candle['x']
  close = candle['c']

  if is_candle_closed:
    print("The candle closed at {}".format(close))
    closes.append(float(close))
    print("Closes")
    print(closes)

    if len(closes) > 15:
        np_closes = np.array(closes)
        rsi = talib.RSI(np_closes, timeperiod=RSI_PERIOD)
        print("All rsi calculated so far")
        print(rsi)
        last_rsi = rsi[-1]
        print("the current rsi is {}".format(last_rsi))

        if last_rsi > RSI_OVERBOUGHT:
            if in_position:
                print("Sell! Sell! Sell!")
                # put a binance sell logic here
                order_successed = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_successed:
                    in_position = False
            else:
                print("We don't own any, nothing to do")
        if last_rsi < RSI_OVERSOLD:
            if in_position:
                print("You are already in a buy position!")
            else:
                print("Buy! Buy! Buy!")
                in_position = True
                # put binance order here
                order_successed = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_successed:
                    in_position = True
  # pprint.pprint(json_message)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()