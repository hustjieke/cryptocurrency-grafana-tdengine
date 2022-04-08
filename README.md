# Visualizing cryptocurrency data with Python, Grafana and TDengine

This is an tutorial that shows how to use Python to fetch cryptocurrency data from Coinbase, store it in TDengine, and visualize the data using Grafana.

# Visualizing time series data

When analyzing streaming data such as cryptocurrency or market metrics, the foundation of the data processing pipeline is efficient storage and queries. To use this data for insights and analytics, data visualization is a convenient way to plot and convey trends, create actionable reports, or even set up alerting.

Most cryptocurrency trading projects will focus on price charts and standard indicators like RSI or moving averages. Derivatives are often overlooked in many cryptocurrency analytics and visualization projects, and there's plenty to explore, such as the underlying pricing metrics such as volatility and funding rates.

A lot of common off-the-shelf tools can plot prices over time, but few are available for derivative features. Having control of the underlying database, creating custom metrics, and building dashboards based on these metrics allows us to build our own solutions with custom pricing inputs and models for derivatives.

In this tutorial, you'll learn how to fetch data from the Coinbase API using a Python script, load the data into TDengine and run SQL queries via TDengine for derivatives insights. We'll be visualizing data using Grafana so that we can build dashboards for reporting or alerts based on metrics you care about.

# Prerequisites

To follow with this tutorial, you'll need the following:

* Coinbase account with an API key

```
api_key: you-key
api_secret: you-secret
```

For more details about coinbase api, see [coinbase develops](https://developers.coinbase.com/docs/wallet)

* install offical coinbase libraries

```
pip install coinbase

# or

easy_install coinbase
```

# Installing TDengine
1. For Debian or Ubuntu, using apt-get to install: 
```
wget -qO - http://repos.taosdata.com/tdengine.key | sudo apt-key add -
echo "deb [arch=amd64] http://repos.taosdata.com/tdengine-stable stable main" | sudo tee /etc/apt/sources.list.d/tdengine-stable.list
echo "deb [arch=amd64] http://repos.taosdata.com/tdengine-beta beta main" | sudo tee /etc/apt/sources.list.d/tdengine-beta.list
sudo apt-get update
apt-cache policy tdengine
sudo apt-get install tdengine
```
For more ways to install, jump to [quick install](https://www.taosdata.com/docs/cn/v2.0/getting-started).

2. Next we should install python driver and connect, jump to [TDengine python driver and connector](https://www.taosdata.com/docs/cn/v2.0/connector#python).

# Table Schema

1. Create a database: cryptocurrency
2. Create a super table: 

We use the next three fixed value fields as tags:

FromCCY = "BTC"

ToCCY = "USD"

exch = "CB"

The super table shema will be like:
```
create stable coinbase(ts timestamp, spot float, sell float, buy float) tags(FromCCY binary(10), ToCCY binary(10), exch binary(10));
```
Then we can create sub table with super table through insert
```
INSERT INTO cryptocurrency.BTC_USD_CB USING coinbase TAGS('BTC', 'USD', 'CB') VALUES ('2022-04-07T10:48:50Z', 1.100000, 1.100000, 1.100000);
```

For more details about table create, link to [taos table](https://www.taosdata.com/docs/cn/v2.0/taos-sql#table)


# Fetching data from Coinbase using Python

For more details you can link to [fetch price data](https://developers.coinbase.com/docs/wallet/guides/price-data)

It requires an authorization token which you should obtain from your Coinbase account. For this tutorial, we'll use a simple Python script to periodically poll the price endpoint. The loop does 3 things:

1. fetch SPOT, SELL, BUY prices and current time from conibase.
2. send the current spot, sell, buy prices and time to TDengine via TDengine python driver.
3. sleep 2 seconds before looping to step 1.

```
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
            # Make the request and get data
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
```

# Run python

Getting the spot price is quite simple. First, let’s take a look at a naked cURL request. Note that you can substitute any supported currency code for USD.

```
curl https://api.coinbase.com/v2/prices/spot?currency=USD
```

Example response:

```
{
  "data": {
    "amount": "43494.56",
    "currency": "USD"
  }
}
```

Now, let’s retrieve the price data using python:

```
$python coinbase-price.py
INSERT INTO cryptocurrency.BTC_USD_CB USING coinbase TAGS('BTC', 'USD', 'CB') VALUES ('2022-04-08T02:42:46Z', 43643.710000, 43882.020000, 43438.410000)
INSERT INTO cryptocurrency.BTC_USD_CB USING coinbase TAGS('BTC', 'USD', 'CB') VALUES ('2022-04-08T02:42:49Z', 43671.060000, 43882.020000, 43438.410000)
INSERT INTO cryptocurrency.BTC_USD_CB USING coinbase TAGS('BTC', 'USD', 'CB') VALUES ('2022-04-08T02:42:52Z', 43671.060000, 43882.020000, 43438.410000)
...
...
```

Use taos shell connect to TDengine, execute select.

```
taos> select * from cryptocurrency.btc_usd_cb;
           ts            |         spot         |         sell         |         buy          |
===============================================================================================
2022-04-08 10:30:18.000 |          43614.17188 |          43842.78125 |          43388.55078 |
2022-04-08 10:30:21.000 |          43610.01953 |          43842.78125 |          43388.55078 |
2022-04-08 10:30:23.000 |          43610.01953 |          43842.78125 |          43388.55078 |
2022-04-08 10:31:32.000 |          43610.53125 |          43816.14062 |          43372.69141 |
...
...
```

# Building a Grafana dashboard

Grafana is an excellent tool for data visualization, and it comes in extremely handy If you're doing any algorithmic trading. The variety of integrations with other services enables you to quickly set up monitoring and alerts for conditions like irregular prices or flow and risk limits.

there are install options covered in the [TDengine Grafana guide](https://www.taosdata.com/docs/cn/v2.0/connections#grafana).
