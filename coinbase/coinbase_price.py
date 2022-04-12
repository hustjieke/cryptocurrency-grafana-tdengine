from coinbase.wallet.client import Client
from time import sleep
import taos

# Set coinbase params
currency_code = 'USD'  # can also use EUR, CAD, etc.
FromCCY = "BTC"
ToCCY = "USD"
Platform = "PLATFORM"

# Get TDengine connection
DB = "cryptocurrency"
HOST = "127.0.0.1"
USER = "root"
PASS = "taosdata"

# SET coinbase api key-secret and api version
KEY = "your-api-key"
KEY_SECRET = "your-key-secret"
API_VERSION = "2022-03-28"

try:
    conn = taos.connect(host=HOST, user=USER, password=PASS, database=DB)
except Exception as e:
    print(e)

if __name__ == '__main__':
    try:
        while 1==1:
            # Make the request 
            client = Client(KEY, KEY_SECRET, api_version=API_VERSION)

            time = client.get_time(api_version=API_VERSION).iso
            spot_price = float(client.get_spot_price(currency=currency_code).amount)
            buy_price = float(client.get_buy_price(currency=currency_code).amount)
            sell_price = float(client.get_sell_price(currency=currency_code).amount)

            sql = "INSERT INTO %s.%s_%s_%s USING coinbase TAGS('%s', '%s', '%s') VALUES ('%s', %f, %f, %f)" % (DB,
                                                                                      FromCCY,
                                                                                      ToCCY,  
                                                                                      Platform,
                                                                                      FromCCY,
                                                                                      ToCCY,  
                                                                                      Platform,
                                                                                      time,   
                                                                                      spot_price,
                                                                                      buy_price,
                                                                                      sell_price)

            print(sql)
            conn.cursor().execute(sql)

            # loop, sleep 2 seconds
            sleep(2)

    except Exception as e:
        print(e)
