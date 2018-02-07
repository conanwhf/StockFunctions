# -*- coding: utf-8 -*-
import os, io, sys, re, datetime
import tushare as ts
import requests
from StockAPIs import *
import itertools

max_decrease = 0
min_increase = 0

def get_history_data(allcode, years):
	res = {}
	for i in allcode:
		res[i] = []
		for year in years:
			start = datetime.date(year, 1, 1)
			end = datetime.date(year, 12, 31)
			data = ts.get_k_data(allcode[i], start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
			try:
				t1 = data.open.iloc[0]
				t2 = data.close.tail(1).iloc[0]
			except:
				print("%d年%s数据不足或有误，按无收益计算"%(year, i))
				t1=t2=1
			#保存当年收益率
			res[i] += [(t2-t1)/t1]
		#print("%s年 %s 收益率为： %s\n" %(years, i, res[i]))
	return res	
	
	
'''
计算筛选可以考虑的投资组合
'''
def cal_case_increase(persent, increase, count):
	res = []
	#某个指数配置过多，不考虑
	if max(persent.values()) > 40:
		return []
	#配置不够多样化，不考虑
	if len(set(persent.values())) <=3:
		return []
	for i in range(0,count):
		temp = 0
		for code in increase:
			temp += persent[code]*increase[code][i]
		#如果某年亏损率过高，不考虑
		if temp < max_decrease:
			return []
		res += [temp]
	#如果n年平均收益率过小，不考虑
	if sum(res)<count*min_increase:
		return []
	else:
		return res


def ETFsimulator(allcode, years):
	#计算历年不同指数的收益率
	increase = get_history_data(allcode, years)
	print(increase)
	plot_data(years, data=list(increase.values()),labels=list(increase.keys()), title=u'历年不同指数的收益率', show=False)

	#生成所有case，将100%分配给不同的指数
	x = itertools.combinations_with_replacement(allcode.keys(), 10)
	res = []
	for case in list(x):
		#persent = dict(zip(allcode.keys(), [0]*len(allcode)))
		persent = dict.fromkeys(allcode.keys(), 0.0)
		for i in case:
			persent[i] += 10
		#print(persent)
		temp = cal_case_increase(persent, increase, count=len(years))
		if temp!=[]:
			print(persent)
			print(temp)
			res += [temp]
	print(len(res))
	#plot_data(years, data=res, labels=['???']*len(res),title=u'符合条件的case', show=True)


if __name__ == "__main__":
	allcode ={'黄金': '518800',	'沪深300': '510300',	
				'创业板': '159915', '央企': '510060', '医药': '512010', 
				'上证50': '000016',	'纳指': '513100',	'标普': '513500', 
				'恒指': '513600'}
				#'中证500': '510500',	
	year_range=range(2013,2018)
	max_decrease = -5 #挑选时允许的最大亏损率（5%）
	min_increase = 18 #挑选时允许的最小平均收益率（18%）
	ETFsimulator(allcode, year_range)
	
