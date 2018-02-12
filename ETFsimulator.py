# -*- coding: utf-8 -*-
import os, io, sys, re, datetime
import tushare as ts
import requests
from StockAPIs import *
import itertools
import json

HistoryDataFile = "history.json"

max_decrease = 0
min_increase = 0

def get_history_data(allcode, years, byFile=False):
	res = {}
	if byFile==True:
		f = open(HistoryDataFile, 'r' ,encoding="utf8")
		data = json.loads(f.read())
		f.close()
		for i in allcode:
			res[i] = data[i]
		return res
	else:
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
		#将获取的数据保存成文件
		f = open(HistoryDataFile, 'w', encoding="utf8")
		f.write(json.dumps(res, ensure_ascii=False))
		f.close()
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
	increase = get_history_data(allcode, years, byFile=True)
	print(increase)
	plot_data(years, data=list(increase.values()),labels=list(increase.keys()), title=u'历年不同投资方向的收益率', show=False)
	#计算历年不同指数的累计现值
	value ={}
	for i in increase:
		temp = 1.0
		value[i] =[]
		for j in increase[i]:
			temp += temp*j
			value[i] += [temp]
	print(value)
	plot_data(years, data=list(value.values()),labels=list(value.keys()), title=u'历年投资指数的累计现值（基准为1.0）', show=False)

	#生成所有case，将100%分配给不同的指数
	x = itertools.combinations_with_replacement(allcode.keys(), 10)
	res = []
	solution = []
	for case in list(x):
		persent = dict.fromkeys(allcode.keys(), 0.0)
		for i in case:
			persent[i] += 10
		#print(persent)
		temp = cal_case_increase(persent, increase, count=len(years))
		if temp!=[]:
			print(persent)
			print(temp)
			res += [temp]
			solution += [persent]
	print(len(res))
	if res==[]:
		print("没有找到符合条件的选择，退出")
		return []
	#将配置内容作为每个case的标签
	labels = []
	for temp in solution:
		st = ''
		for j in temp:
			if temp[j]>0:
				st += "%s:%d "%(j,int(temp[j]))
		labels += [st]
	plot_data(years, data=res, labels=labels, title=u'符合条件的case', show=True)
	return solution


if __name__ == "__main__":
	allcode ={	'上证':'000001', 	'深成指':'399001', 	'创业板': '159915', 
				'沪深300': '399300', '中证500': '000905', '上证50': '000016',
				'上证中小':'000046', 	'上证央企': '000042', '国企':'000056', 
				'TMT50':'399610', 	'白酒': '399997', 	'医药': '000037',
				'能源':'000032', 	'地产':'000006', 	'工业':'000034',
				'金融':'000038', 
				'纳指': '513100', 	'标普': '513500', 	'恒指': '513600',
				#'国债':'000012', 	'黄金':'518800'
				}
			#'上证':'000001', '深成指':'399001', '创业板': '159915', 
			#'沪深300': '399300', '中证500': '000905', '上证50': '000016',
			#'上证中小':'000046', '上证央企':'000042', '国企':'000056', 
			#'TMT50':'399610', '白酒': '399997', '医药': '000037',
			#'能源':'000032', '地产':'000006', '工业':'000034',
			#'金融':'000038', 
			#'纳指': '513100', '标普': '513500', '恒指': '513600',
			#'国债':'000012', '黄金':'518800'	
		
	year_range=range(1998,2019)
	max_decrease = -5 #挑选时允许的最大亏损率（3%）
	min_increase = 10 #挑选时允许的最小平均收益率（18%）
	ETFsimulator(allcode, year_range)
	
