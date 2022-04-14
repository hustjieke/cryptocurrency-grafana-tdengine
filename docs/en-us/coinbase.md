Table of Contents
=================

   * [Prepare](#prepare)
   * [Prepare Database and Table](#prepare-database-and-table)
   * [Fetch data from Coinbase](#fetch-data-from-coinbase)
   * [Building a dashboard based on Grafana](#building-a-dashboard-based-on-grafana)

[Coinbase Official Website](https://www.coinbase.com)

# Prepare

1. Create [Coinbase account](https://www.coinbase.com/signup) and ensure [API Key Pair](https://www.coinbase.com/signin), it will be used latter.

2. Install pip

```
python -m ensurepip
```

3. Install [Coinbase Library](https://developers.coinbase.com/docs/wallet/client-libraries):

```
pip install coinbase

# or

easy_install coinbase
```

4. Install TDengine (version >= 2.4) by [apt-get](https://tdengine.com/docs/en/v2.0/getting-started#install-tdengine-by-apt-g), [Source code](https://tdengine.com/docs/en/v2.0/getting-started#install-from-source) or [Package](https://tdengine.com/docs/en/v2.0/getting-started#install-from-package).

After install success, [start taosd and taosadapter](https://tdengine.com/docs/en/v2.0/getting-started#quick-launch).

```
systemctl start taosd
systemctl start taosadapter
```

Check service status.

```
systemctl status taosd
systemctl status taosadapter
```

5. Install [TDengine Python Connector](https://tdengine.com/docs/en/v2.0/connector#python).

# Prepare Database and Table

* [Create a database](https://tdengine.com/docs/en/v2.0/taos-sql#management), let's create a database named `cryptocurrency`:

```
CREATE DATABASE cryptocurrency;
```

* [Create super table](https://tdengine.com/docs/en/v2.0/taos-sql#stable-management)

Set three column fields as TAGS:
`FromCCY`: currency from.
`ToCCY`: currency to.
`Platform`: Trade platform like `coinbase`, `binance`, etc.

The column fields of table:
`ts`: timestamp
`spot`: live price
`sell`: sell(bid) price
`buy`: buy(ask) price

```
CREATE STABLE coinbase(ts timestamp, spot float, sell float, buy float) tags(FromCCY binary(10), ToCCY binary(10), Platform binary(10));
```

* Create Subtable

Insert data by [Auto create based on super table](https://tdengine.com/docs/en/v2.0/taos-sql#data-writing):

```
INSERT INTO cryptocurrency.BTC_USD_coinbase USING coinbase TAGS('BTC', 'USD', 'CB') VALUES ('2022-04-07T10:48:50Z', 1.100000, 1.100000, 1.100000);
```

# Fetch data from Coinbase

[Coinbase API](https://developers.coinbase.com/api/v2#introduction) provides the method on how to access to [market trade and price data](https://developers.coinbase.com/docs/wallet/guides/price-data). Let's make requests to get price data from provided endpoint and write data to TDengine.

* Get timestamp spot, sell and buy prices from Coinbase.
* Write data into TDengine.
* Loop per second.

```
from coinbase.wallet.client import Client
from time import sleep
import taos

# Set coinbase params
currency_code = 'USD'  # can also use EUR, CAD, etc.
FromCCY = "BTC"
ToCCY = "USD"
Platform = "coinbase"

# Get TDengine connection
DB = "cryptocurrency"
HOST = "127.0.0.1"
USER = 'root'
PASS = 'taosdata'

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
            sleep(1)

    except Exception as e:
        print(e)
```

* Run Python scripts:

```
$python coinbase-price.py
INSERT INTO cryptocurrency.BTC_USD_coinbase USING coinbase TAGS('BTC', 'USD', 'coinbase') VALUES ('2022-04-08T02:42:46Z', 43643.710000, 43882.020000, 43438.410000)
INSERT INTO cryptocurrency.BTC_USD_coinbase USING coinbase TAGS('BTC', 'USD', 'coinbase') VALUES ('2022-04-08T02:42:49Z', 43671.060000, 43882.020000, 43438.410000)
INSERT INTO cryptocurrency.BTC_USD_coinbase USING coinbase TAGS('BTC', 'USD', 'coinbase') VALUES ('2022-04-08T02:42:52Z', 43671.060000, 43882.020000, 43438.410000)
...
...
```

Using [TDengine Shell Cmd Line](https://tdengine.com/docs/en/v2.0/getting-started#tdengine-shell-command-li) connect to TDengine and make a query:

```
taos> select * from cryptocurrency.btc_usd_platform;
           ts            |         spot         |         sell         |         buy          |
===============================================================================================
2022-04-08 10:30:18.000 |          43614.17188 |          43842.78125 |          43388.55078 |
2022-04-08 10:30:21.000 |          43610.01953 |          43842.78125 |          43388.55078 |
2022-04-08 10:30:23.000 |          43610.01953 |          43842.78125 |          43388.55078 |
2022-04-08 10:31:32.000 |          43610.53125 |          43816.14062 |          43372.69141 |
...
...
```

# Building a dashboard based on Grafana

* Install Grafana and [Config Grafana wiht TDengine plugin](https://tdengine.com/docs/en/v2.0/connections#grafana)

* [Create Dashboard](https://tdengine.com/docs/en/v2.0/connections#create-dashboard)

* Input SQL:

```
select avg(spot_price) as spot, avg(bid_price) as book_sell, avg(ask_price) as book_buy from cryptocurrency.binance where ts >= $from and ts < $to interval($interval)；
```

Ref from [Create Dashboard](https://tdengine.com/docs/en/v2.0/connections#create-dashboard).

> INPUT SQL: Enter the statement to query (the result set of the SQL statement should be two columns and multiple rows), for example: select avg(mem_system) from log.dn where ts >= $from and ts < $to interval($interval) , where from, to and interval are built-in variables of the TDengine plug-in, representing the query range and time interval obtained from the Grafana plug-in panel. In addition to built-in variables, it is also supported to use custom template variables.

e.g.:
```
select avg(sell) as sell, avg(buy) as buy, avg(spot) from cryptocurrency.coinbase where ts > '2022-04-02 14:10:00' and ts < '2022-4-31 18:40:00' and fromCCY='BTC' and toCCY='USD' and platform='coinbase' interval(10s);
```

![](../images/coinbase_btcusd.png)
