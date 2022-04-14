[English](README.md) | 简体中文

[加密货币](https://en.wikipedia.org/wiki/Cryptocurrency) 是不依赖于银行系统的数字货币中的一种，人们普遍关注它的实时价格，实时价格是典型的时间序列数据。

[TDengine](https://www.taosdata.com) 是一款支持 SQL 的高性能、可扩展时序数据库，可以将加密货币的实时价格从各个交易平台读取并存储到 TDengine 并进行高效的查询分析，借助 [Grafana](https://grafana.com/) 面板展示其价格曲线。甚至借助相关工具预测未来的走势。

本项目用于从各个平台获取交易数据 demo 演示, 每个加密货币交易平台对应一个目录

* [基于 TDengine-grafana-coinbase 的加密货币可视化示例](docs/zh-cn/coinbase_zh.md)

* [基于 TDengine-grafana-binance 的加密货币可视化示例](docs/zh-cn/binance_zh.md)
