[English](README.md) | 简体中文

[加密货币](https://en.wikipedia.org/wiki/Cryptocurrency) 中的价格走势普通受到人们的关注，它是典型的时间序列数据。

[TDengine](https://www.taosdata.com) 是一款高性能、可扩展的时序数据库，可以将加密货币的价格数据从各个交易平台读取并存储到 TDengine 中。借助 [Grafana](https://grafana.com/) 展示其价格走势，也可以从 TDengine 中读出数据用于后续高效的>查询分析，甚至借助相关工具预测其未来的走势。

本项目用于从各个平台获取交易数据 demo 演示, 每个加密货币交易平台对应一个目录

* [基于 TDengine-grafana-coinbase 的加密货币可视化示例](docs/zh-cn/coinbase_zh.md)

* [基于 TDengine-grafana-binance 的加密货币可视化示例](docs/zh-cn/binance_zh.md)
