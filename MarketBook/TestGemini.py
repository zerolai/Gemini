import websocket
import json
import time
import MarketBook

def on_open(ws):
    print("CONNECTED")

def on_close(ws):
    print("DISCONNECTED")

def on_message(ws, message):
    msg_dict = json.loads(message)
    if msg_dict['type'] == 'update':
        events = msg_dict['events']
        for event in events:
            if event['type'] == 'change':
                bookBTCUSD.processChange(event)
            elif event['type'] == 'trade':
                bookBTCUSD.processTrade(event)

    bookBTCUSD.printBook(10, True)


#main
bookBTCUSD = MarketBook.GeminiBook('btcusd')
ws = websocket.WebSocketApp("wss://api.gemini.com/v1/marketdata/BTCUSD", on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever(ping_interval=5)
time.sleep(3)
print('end')