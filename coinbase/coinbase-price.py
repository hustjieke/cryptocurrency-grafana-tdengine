from coinbase.wallet.client import Client
from time import sleep

currency_code = 'USD'  # can also use EUR, CAD, etc.

if __name__ == '__main__':
    try:
        while 1==1:
            client = Client("you-key", "you-key-secret", api_version='2022-03-22')
            # Make the request
            spot_price = client.get_spot_price(currency=currency_code)
            buy_price = client.get_buy_price(currency=currency_code)
            sell_price = client.get_sell_price(currency=currency_code)
            time = client.get_time(api_version='2022-03-22')

            print ('Current spot bitcoin price in %s: %s' % (currency_code, spot_price.amount))
            print ('Current buy bitcoin price in %s: %s' % (currency_code, buy_price.amount))
            print ('Current sell bitcoin price in %s: %s' % (currency_code, sell_price.amount))
            print ('time: %s' %time.iso)
            sleep(2)

    except Exception as e:
        print(e)
