# -*- coding: utf-8 -*-

import os, io, sys, re, datetime
import requests
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import random

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
def revise_date(start, end):
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
对几个数组绘制折线图
'''
def plot_data(x=[], data=[[]], labels=[], title = "T=???", show=False):
	#计算需要的中间变量
	count = len(data)
	if count == 0:
		print("待绘制数据为空！")
		return
	if labels==[]:
		print("自动生成数据的labels")
		for i in range(count):
			labels += ["%04d"%i]
	if count!=len(labels):
		print("数据名称和数据数组个数不符，无法绘制")
		return
	length = []
	alldata = []
	for i in range(count):
		length += [len(data[i])]
		alldata += data[i]
	dataMin = min(alldata)
	dataMax = max(alldata)	
	lenMax = max(length)
	#生成颜色数据
	if count<=7:
		colors="bgryckm"
	else:
		colors = []
		for i in range(count):
			random.seed()
			(r,g,b)=random.randint(0,0x7f), random.randint(0x7f,0xff), random.randint(0,0xff)
			if i%3==0:
				colors += [ '#%02x%02x%02x'%(r,g,b)]
			if i%3==1:
				colors += [ '#%02x%02x%02x'%(b,r,g)]
			if i%3==2:
				colors += [ '#%02x%02x%02x'%(g,b,r)]
			#colors += [ '#%06x' %random.randint(0,0xf0f0f0)]
	#折线图初始化配置	
	#colors="bgryckm"
	plt.rcParams['font.sans-serif'] = ['SimHei']  # for Chinese characters
	plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
	fig,ax = plt.subplots()
	plt.title(title)
	plt.grid(True)
	#定义x, y的坐标轴
	ax.set_ylim([dataMin-(dataMax-dataMin)*0.1,dataMax+(dataMax-dataMin)*0.1])    
	if x==[] or len(x)!=lenMax:
		x= range(lenMax)
	#绘制
	for i in range(count):
		plt.plot(x[0:length[i]], data[i], "o-",label=labels[i], color=colors[i])
	plt.legend(loc='best')
	plt.close(0)
	if show==True:
		plt.show()
	return

'''
A=[1,2,3,4,5]
B=[5,6,3,4,8,1,-2]
C=[0.1, 0.4, 10]
x=[4,5,6,7,8,9,10]
plot_data(x, data=[B,C,A],labels=["B", "C","A"], title=u'测试', show=True)
'''