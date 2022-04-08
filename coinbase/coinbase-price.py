from coinbase.wallet.client import Client
from time import sleep
import taos

# Set coinbase params
currency_code = 'USD'  # can also use EUR, CAD, etc.
FromCCY = "BTC"
ToCCY = "USD"
exch = "CB"

# Get TDengine connection
db = "cryptocurrency"
try:
    conn = taos.connect(host='45.120.216.240', user='root', password='taosdata', database=db)
except Exception as e:
    print(e)

if __name__ == '__main__':
    try:    
        while 1==1:
            # Make the request 
            client = Client("your-api-key", "your-key-secret", api_version='2022-03-22')

            time = client.get_time(api_version='2022-03-22').iso
            spot_price = float(client.get_spot_price(currency=currency_code).amount)
            buy_price = float(client.get_buy_price(currency=currency_code).amount)
            sell_price = float(client.get_sell_price(currency=currency_code).amount)

            sql = "INSERT INTO %s.%s_%s_%s USING coinbase TAGS('%s', '%s', '%s') VALUES ('%s', %f, %f, %f)" % (db,
                                                                                      FromCCY,
                                                                                      ToCCY,  
                                                                                      exch,   
                                                                                      FromCCY,
                                                                                      ToCCY,  
                                                                                      exch,   
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
