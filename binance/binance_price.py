import requests
from time import sleep
import taos

# Currently we support 5 cryptocurrency to USD
PLATFORM = "binance"
SYMBOLS_SIZE = 5
SYMBOLS = '["BTCUSD","ETHUSD","LTCBTC","BCHUSD","DOGEUSD"]'
PRICE_URL = 'https://api.binance.us/api/v3/ticker/price?symbols='
BEST_ORDER_BOOK_PRICE_URL = 'https://api.binance.us/api/v3/ticker/bookTicker?symbols='

# TDengine connection args
DB = "cryptocurrency"
HOST = "127.0.0.1"
USER = "root"
PASS = "taosdata"

# Get TDengine connection
def get_conn():
        return taos.connect(host=HOST, user=USER, password=PASS, database=DB)
              
if __name__ == '__main__':
    price_url = PRICE_URL + SYMBOLS
    best_order_book_price_url = BEST_ORDER_BOOK_PRICE_URL + SYMBOLS
    conn = get_conn()

    try:
        while 1 == 1:

            # Get binance server time: {"serverTime":1649775807821}
            respTime = requests.get('https://api.binance.us/api/v3/time')
            serverTime = respTime.json()['serverTime']
   
            # resp: [{'symbol': 'BTCUSD', 'price': '40130.3000'}, {'symbol': 'ETHUSD', 'price': '3015.1800'},...]
            ticker_price = requests.get(price_url).json()
            # resp: [{'symbol': 'BTCUSD', 'bidPrice': '40120.5700', 'bidQty': '0.20000000', 'askPrice': '40125.2600', 'askQty': '0.01246300'},...]
            best_order_book_price = requests.get(best_order_book_price_url).json()

            for idx in range (SYMBOLS_SIZE):
                sym = ticker_price[idx]['symbol']
                table = DB + "." + PLATFORM + "_" + sym
                sql = "INSERT INTO %s USING binance TAGS('%s', '%s') VALUES (%s, %f, %f, %f, %f, %f)" % (table,
                                                                                                     sym,
                                                                                                     PLATFORM,
                                                                                                     serverTime,
                                                                                                     float(ticker_price[idx]['price']),
                                                                                                     float(best_order_book_price[idx]['bidPrice']),
                                                                                                     float(best_order_book_price[idx]['bidQty']),
                                                                                                     float(best_order_book_price[idx]['askPrice']),
                                                                                                     float(best_order_book_price[idx]['askQty']))
                conn.cursor().execute(sql)
                sleep(1)
    except Exception as e:
        print(e)
