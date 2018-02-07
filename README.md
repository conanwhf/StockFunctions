# StockFunctions
自留地，一些股票相关的数据分析，数据获取均使用tushare库。

## 安装用到的库
	先安装pip，之后安装以下的库：
	
		pip3 install requests
		pip3 install lxml
		pip3 install pandas
		pip3 install bs4
		pip3 install tushare
		sudo apt-get install python3-tk
		pip3 install matplotlib


## 公用函数文件
1. StockAPIs，通用API文件
	- `get_stock_codes_tushare`，从tushare API 获取所有股票列表信息
	- `revise_date`，用开盘日校准起始和结束日期
	- `plot_data`，绘制折线图，在一张图上画n个数组的数据，共用横座标


## 解决、讨论特定问题
1. ETFsimulator，指数&ETF历史收益模拟
2. CheckAllRaise，列举一段时间内所有股票的涨幅
3. CheckAllNew，检查次新股打开涨停板后K天之内的表现
