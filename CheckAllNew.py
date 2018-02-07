# -*- coding: utf-8 -*-
import os, io, sys, re, datetime
import tushare as ts
import requests
from StockAPIs import *

'''
检查次新股打开涨停板后的表现
'''
def check_all_new(start_str, end_str):
	KeepDays = 5
	stocks = get_stock_codes_tushare(byFile=False)
	start_t = int(start_str)*100
	end_t = int(end_str)*100+32
	if datetime.datetime.now().strftime('%Y%m') == end_str:
		#当月新股拿不到日期，特殊处理
		stocks = stocks[(stocks['timeToMarket']==0) | ( (stocks['timeToMarket']>start_t) & (stocks['timeToMarket']<end_t))]
	else:
		stocks = stocks[(stocks['timeToMarket']>=start_t) & (stocks['timeToMarket']<=end_t)]
	#print(stocks.timeToMarket)

	#查询所有新股数据
	start = datetime.datetime.strptime(start_str+'01', "%Y%m%d")
	end = datetime.datetime.strptime(end_str+'01', "%Y%m%d") + datetime.timedelta(days=30+KeepDays*2+20) #保证至少获取上市30天后的数据
	allcode = stocks.index.values
	result = pd.DataFrame(columns=['code', 'timeToMarket', 'openDate','after2close','after12close','raise'])
	
	# 遍历所有新股，判断是否符合要求
	for i in allcode:
		data = ts.get_k_data(i, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
		if data.empty:
			print('No data for code %s-%s' %(i,stocks.name[i]))
			continue
		#检查打开涨停板时间
		for j in data.index:
			if j==0:
				continue
			temp1 = float(data.ix[j].close)/float(data.ix[j-1].close)
			temp2 = float(data.ix[j].low)/float(data.ix[j-1].close)
			if temp1 < 1.097 or temp2 < 1.097: #收盘或中途打开涨停板
				print("today=%f, yesterday=%f, temp1=%f, temp2=%f" %(data.ix[j].close, data.ix[j-1].close, temp1, temp2))
				print("新股 %s-%s 在 %s 打开了涨停板, index=%d" %(i, stocks.name[i], data.ix[j].date, j))
				break
		# 记录打开涨停后情况
		if (j+2+KeepDays >= len(data)):
			print("可观察数据不够，跳过")
		else:
			appData = pd.DataFrame({'code':i, 'timeToMarket':[stocks.timeToMarket[i]], 'openDate':[data.ix[j].date], 'after2close':[data.ix[j+2].close], 'after12close':[data.ix[j+2+KeepDays].close],'name':[stocks.name[i]]})
			appData['raise']="%.2f%%" %((data.ix[j+2+KeepDays].close-data.ix[j+2].close)*100/data.ix[j+2].close)
			result=pd.concat([result,appData])
	
	#按照升值排序，保存
	result.sort_values(by=['raise'],ascending=[0],inplace=True)
	result = result.reset_index(drop=True)
	print(result)
	result.to_csv("new%s-%s.csv" %(start_str, end_str), sep=',', header=True, columns=['code', 'name', 'timeToMarket', 'openDate', 'after2close', 'after12close', 'raise'])
	return 0



if __name__ == "__main__":
	check_all_new("201701", "201707")
	exit(0)
