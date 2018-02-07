# -*- coding: utf-8 -*-
import os, io, sys, re, datetime
import tushare as ts
import requests
from StockAPIs import *

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

if __name__ == "__main__":
	start = datetime.date(2007, 4, 30)
	end = datetime.date(2010, 4, 30)
	check_all_raise(start, end)
	exit(0)
