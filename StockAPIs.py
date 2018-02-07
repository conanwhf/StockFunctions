# -*- coding: utf-8 -*-

import os, io, sys, re, datetime
import requests
import tushare as ts
import pandas as pd

''' 
从tushare API 获取所有股票列表信息
'''
def get_stock_codes_tushare(byFile=False):
	StockCodesFile = 'codes.csv'
	# 强制从文件获取数据
	if byFile==True:
		stocks = pd.read_csv(StockCodesFile, sep=',', dtype={'code':object})
		stocks.set_index('code', inplace=True, drop=True)
		if stocks.empty:
			print("获取股票代码信息失败！")
			return []
		else:
			return stocks
	# 从网络获取数据
	try:
		stocks = ts.get_stock_basics()
		stocks.to_csv(StockCodesFile, sep=',', header=True)
		return stocks
	except:
		info=sys.exc_info()  
		print (info[0],":",info[1])
		return hy_get_stock_codes_tushare(byFile=True)


'''
用开盘日校准起始和结束日期
'''
def ReviseDate(start, end):
	#判断start, end是否开盘日
	opendays = ts.trade_cal()
	while True:
		start_is_open = opendays[opendays.calendarDate == start.strftime('%Y-%m-%d')]
		end_is_open = opendays[opendays.calendarDate == end.strftime('%Y-%m-%d')]
		if start_is_open.empty or start_is_open['isOpen'].values == 0:
			#print("开始日期%s不是开盘日，尝试后一天" % start.strftime('%Y-%m-%d'))
			start = start + datetime.timedelta(days=1)
			continue
		if end_is_open.empty or end_is_open['isOpen'].values == 0:
			#print("结束日期%s不是开盘日，尝试前一天" % end.strftime('%Y-%m-%d'))
			end = end - datetime.timedelta(days=1)
			continue
		print("开始日期：%s, 结束日期：%s" %(start, end))
		break	
	return (start, end)

'''
检查一段时间内所有股票的涨幅
'''
def check_all_raise(start, end):
	#判断start, end是否开盘日
	opendays = ts.trade_cal()
	while True:
		start_is_open = opendays[opendays.calendarDate == start.strftime('%Y-%m-%d')]
		end_is_open = opendays[opendays.calendarDate == end.strftime('%Y-%m-%d')]
		if start_is_open.empty or start_is_open['isOpen'].values == 0:
			print("开始日期%s不是开盘日，尝试后一天" % start.strftime('%Y-%m-%d'))
			start = start + datetime.timedelta(days=1)
			continue
		if end_is_open.empty or end_is_open['isOpen'].values == 0:
			print("结束日期%s不是开盘日，尝试前一天" % end.strftime('%Y-%m-%d'))
			end = end - datetime.timedelta(days=1)
			continue
		print("开始日期：%s, 结束日期：%s" %(start, end))
		break

	# 修正日期后，初始化
	start_str = start.strftime('%Y-%m-%d')
	end_str = end.strftime('%Y-%m-%d')
	stocks = get_stock_codes_tushare(byFile=False)
	allcode = stocks.index.values
	#allcode=['000008','600202', '000923']
	result = pd.DataFrame(columns=['code', start_str, end_str, 'raise', 'name','industry'])
	
	# 遍历所有股票，判断是否符合要求
	for index, i in enumerate(allcode):
		try:
			data1 = ts.get_k_data(i, start=start_str, end=start_str)
			data2 = ts.get_k_data(i, start=end_str, end=end_str)
			if data1.empty or data2.empty:
				print('%d-No data for code %s' %(index, i))
				continue
		except:
			continue
		before = float(data1.close.iloc[0])
		now = float(data2.close.iloc[0])
		appendData=pd.DataFrame({'code':i, start_str:[before], end_str:[now], 'raise':[now/before], 'name':[stocks.name[i]], 'industry':[stocks.industry[i]]}, index=[index])
		print(appendData)
		result=pd.concat([result,appendData])
	
	#按照升值排序，保存
	result.sort_values(by=['raise'],ascending=[0],inplace=True)
	result = result.reset_index(drop=True)
	print(result)
	result.to_csv("%s-%s.csv" %(start.strftime('%Y%m%d'), end.strftime('%Y%m%d')),sep=',',header=True)
	return 0


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


''' 指数&ETF历史收益模拟 
'''
def ETFsimulator(allcode, persent):
	for year in range(2013,2018):
		total = 0
		start = datetime.date(year, 1, 1)
		end = datetime.date(year, 12, 31)
		#(start, end) = ReviseDate(start, end)
		print(start, end)
		for i in allcode:
			data = ts.get_k_data(allcode[i], start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
			try:
				t1 = data.open.iloc[0]
				t2 = data.close.tail(1).iloc[0]
			except:
				#print(data)
				print("%d年%s数据不足或有误，按无收益计算"%(year, i))
				t1=t2=1
			temp = (t2-t1)*100/t1
			total += persent[i]*temp
			print("%s:\t\t%f\t%f\t%f%%" %(i, t1, t2, temp))
		print("%d 年综合收益率为： %.2f%%\n" %(year, total))

