# -*- coding: utf-8 -*-
import os, io, sys, re, datetime
import tushare as ts
import requests
from StockAPIs import *

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


if __name__ == "__main__":
	'''ETF历史收益模拟
	allcode ={'黄金': '518800',	'沪深300': '510300',	'中证500': '510500',	
				'创业板': '159915', '央企': '510060', '医药': '512010', 
				'国债': '511010',	'纳指': '513100',	'标普': '513500', 
				'恒指': '513600'}
	persent ={'黄金': 0.1, '沪深300': 0.1, '中证500': 0.3, '国债': 0.0, '恒指': 0.1,
				'纳指': 0.1,	'标普': 0.2, '创业板':0.0, '央企': 0.1, '医药':0.0}
	print("比例分配：", persent)
	ETFsimulator(allcode, persent)
	exit(0)
	'''