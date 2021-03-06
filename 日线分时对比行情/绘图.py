# -*- coding: utf-8 -*-



import sys
import os
import pickle
import copy
import datetime
import numpy
from PyQt5 import *
import PyQt5
import sys
import random

import matplotlib
matplotlib.use("Qt5Agg")


import matplotlib.pyplot as pyplot
import matplotlib.ticker as ticker



import Public.Public as Public



from 子图定义.公司信息子图 import 公司信息子图
from 子图定义.日线价格子图 import 日线价格子图
from 子图定义.日线换手子图 import 日线换手子图
from 子图定义.分时价格子图 import 分时价格子图
from 子图定义.分时手数子图 import 分时手数子图
from 子图定义.实盘价格子图 import 实盘价格子图
from 子图定义.实盘手数子图 import 实盘手数子图



__color_pink__= '#ffc0cb'
__color_navy__= '#000080'
__color_gold__= '#fddb05'

__横轴倍率__= 10.0 / 230.0
__纵轴倍率__= 0.3





class 分时行情图系:
	'''

	'''

	def __init__(self, parent, 目标日期, 绘图数据):
		'''

		'''
		self._parent= parent		# 分时大图区块 对象
		self._ilogger= Public.IndentLogger(logger=parent._ilogger._logger, indent=parent._ilogger._indent+1)

		# 当日数据
		当日数据= 绘图数据['分时数据'][目标日期]
		self._目标日期= 目标日期
		self._时间常数= 当日数据['时间常数']

		#	横轴参数（分时价格 与 分时手数 共用，所以放在这里）
		#===================================================================================================
		self._横轴参数= self.计算横轴参数()

		#	个股行情
		#===================================================================================================
		if 当日数据['个股行情有效']:
			# 分时数据
			个股分时行情= 当日数据['个股分时行情']
			self._个股时间序列= 个股分时行情['时间序列']	# 成员是 datetime.datetime 对象

			# 分时行情坐标序列
			self._个股调整时间= self.计算调整时间序列(时间序列=self._个股时间序列)
			self._个股坐标序列= self.计算调整时间序列坐标(调整时间序列=self._个股调整时间)

		#	子图对象
		#===================================================================================================
		self._分时价格子图= 分时价格子图(parent=self, 目标日期=目标日期, 绘图数据=绘图数据)
		self._分时手数子图= 分时手数子图(parent=self, 目标日期=目标日期, 绘图数据=绘图数据)

		#	衬底平面
		#===================================================================================================
		self._衬底平面= None



	def 计算横轴参数(self):
		'''

		'''
		时间常数= self._时间常数

		上午开始时间= 时间常数['上午开始']
		上午结束时间= 时间常数['上午结束']
		下午开始时间= 时间常数['下午开始']
		下午结束时间= 时间常数['下午结束']
		dtc_092500=   时间常数['09:25:00']
		dtc_093000=   时间常数['09:30:00']
		dtc_130000=   时间常数['13:00:00']

		# XXX: 这些内容只能在各个图系里分别计算，因为只有带具体日期的 datetime.datetime 对象才支持减法操作
		横轴参数= {}
		横轴参数['左侧裕量']= 30.0
		横轴参数['右侧裕量']= 30.0
		横轴参数['坐标起点']= -横轴参数['左侧裕量']
		横轴参数['坐标终点']= ((上午结束时间-上午开始时间) + (下午结束时间-下午开始时间)).total_seconds() + 横轴参数['右侧裕量']
		午间时差= 下午开始时间-上午结束时间
		横轴参数['午间时差']= 午间时差
		横轴参数['横轴尺寸']= 横轴参数['坐标终点'] - 横轴参数['坐标起点']
		横轴参数['横轴倍率']= 2.0 / 2300.0
		横轴参数['横轴宽度']= 横轴参数['横轴尺寸'] * 横轴参数['横轴倍率']

		# 计算主坐标点
		#--------------------------------------------------------------------------------------------------------------
		上午主标时间= [时间 for 时间 in [dtc_093000 + datetime.timedelta(minutes=15*i) for i in range(9)] \
				if 时间 >= 上午开始时间 and 时间 <= 上午结束时间]
		上午主坐标值= [(时间-上午开始时间).total_seconds() for 时间 in 上午主标时间]

		下午主标时间= [时间 for 时间 in [dtc_130000 + datetime.timedelta(minutes=15*i) for i in range(9)] \
				if 时间 >= 下午开始时间 and 时间 <= 下午结束时间]
		下午主坐标值= [(时间-午间时差-上午开始时间).total_seconds() for 时间 in 下午主标时间]

		主标时间序列= 上午主标时间 + 下午主标时间
		主坐标值序列= 上午主坐标值 + 下午主坐标值

		# 计算副坐标点
		#--------------------------------------------------------------------------------------------------------------
		上午副标时间= [时间 for 时间 in [dtc_092500 + datetime.timedelta(minutes=5*i) for i in range(25)] \
				if 时间 >= 上午开始时间 and 时间 <= 上午结束时间 and 时间 not in 上午主标时间]
		上午副坐标值= [(时间-上午开始时间).total_seconds() for 时间 in 上午副标时间]

		下午副标时间= [时间 for 时间 in [dtc_130000 + datetime.timedelta(minutes=5*i) for i in range(25)] \
				if 时间 >= 下午开始时间 and 时间 <= 下午结束时间 and 时间 not in 下午主标时间]
		下午副坐标值= [(时间-午间时差-上午开始时间).total_seconds() for 时间 in 下午副标时间]

		副标时间序列= 上午副标时间 + 下午副标时间
		副坐标值序列= 上午副坐标值 + 下午副坐标值

		主标表示序列= [时间.strftime('%H:%M') for 时间 in 主标时间序列]
		副标表示序列= [时间.strftime('%H:%M') for 时间 in 副标时间序列]

		横轴参数['主标时间']= 主标时间序列
		横轴参数['副标时间']= 副标时间序列
		横轴参数['主坐标值']= 主坐标值序列
		横轴参数['副坐标值']= 副坐标值序列
		横轴参数['主标表示']= 主标表示序列
		横轴参数['副标表示']= 副标表示序列

		横轴参数['xMajorLocator']= ticker.FixedLocator( numpy.array(主坐标值序列) )
		横轴参数['xMinorLocator']= ticker.FixedLocator( numpy.array(副坐标值序列) )

		def x_major_formatter(坐标, pos=None):
			偏移= 主坐标值序列.index(坐标)
			return 主标表示序列[偏移]

		def x_minor_formatter(坐标, pos=None):
			偏移= 副坐标值序列.index(坐标)
			return 副标表示序列[偏移]

		xMajorFormatter= ticker.FuncFormatter(x_major_formatter)
		xMinorFormatter= ticker.FuncFormatter(x_minor_formatter)

		横轴参数['xMajorFormatter']= xMajorFormatter
		横轴参数['xMinorFormatter']= xMinorFormatter

		# 计算标注位置
		#--------------------------------------------------------------------------------------------------------------
		横轴参数['标注位置组一']= [坐标 for 表示, 坐标 in zip(主标表示序列, 主坐标值序列) if 表示 in ('09:30', '10:15', '11:00', '13:15', '14:00', '14:45')]
		横轴参数['标注位置组二']= [坐标 for 表示, 坐标 in zip(主标表示序列, 主坐标值序列) if 表示 in ('09:45', '10:30', '11:15', '13:30', '14:15')]
		横轴参数['标注位置组三']= [坐标 for 表示, 坐标 in zip(主标表示序列, 主坐标值序列) if 表示 in ('10:00', '10:45', '11:30', '13:45', '14:30')]

		横轴参数['标注位置']= dict(zip(主标表示序列, 主坐标值序列))

		return 横轴参数



	def 返回图系横轴宽度(self):
		'''

		'''
		return self._横轴参数['横轴宽度']



	def 返回图系纵轴高度(self):
		'''

		'''
		return self._分时价格子图.返回纵轴高度() + self._分时手数子图.返回纵轴高度()



	def 计算调整时间序列(self, 时间序列, 午间时差=None):
		'''
		午间时差 是 datetime.timedelta 对象
		'''
		if 午间时差 is None:
			午间时差= self._横轴参数['午间时差']
		dtc_120000= self._时间常数['12:00:00']
		return [ 时间 if 时间<dtc_120000 else 时间-午间时差 for 时间 in 时间序列 ]



	def 计算调整时间序列坐标(self, 调整时间序列):
		'''

		'''
		上午开始时间= self._时间常数['上午开始']
		return [(时间-上午开始时间).total_seconds() for 时间 in 调整时间序列]



	def 计算纵轴坐标区间(self):
		'''

		'''
		return self._分时价格子图.计算纵轴坐标区间()



	def 计算成交步进记录(self):
		'''

		'''
		return self._分时手数子图.计算成交步进记录()



	def 计算价格子图纵轴参数(self, 坐标区间):
		'''
		坐标区间:
		{
			'个股最高': 45600,
			'个股最低': 12300,
			'指数最高': 3330000,
			'指数最低': 3300000,
		}
		'''
		self._分时价格子图.计算纵轴参数(坐标区间=坐标区间)



	def 计算手数子图纵轴参数(self, 步进记录):
		'''

		'''
		self._分时手数子图.计算纵轴参数(步进记录=步进记录)



	def 图系平面初始化(self, 图片对象, 图系偏移, 全图大小):
		'''
		注意，这里要强调初始化的顺序。指数子图要充当“衬底”的角色，要最先初始化
		'''
		横轴参数= self._横轴参数
		
		#	建立衬底平面
		#=======================================================================================================
		横轴宽度= 横轴参数['横轴宽度']
		手数子图高度= self._分时手数子图.返回纵轴高度()
		纵轴高度= self._分时价格子图.返回纵轴高度() + 手数子图高度

		图系横移, \
		图系纵移= 图系偏移

		全图宽度, \
		全图高度= 全图大小

		布局参数= (图系横移/全图宽度, 图系纵移/全图高度, 横轴宽度/全图宽度, 纵轴高度/全图高度)
		衬底平面= 图片对象.add_axes(布局参数, axis_bgcolor='black')
		#	衬底平面.set_frame_on(False)	# XXX: for debugging ... ...

		# 设置横轴坐标范围
		横标起点, 横标终点= 横轴参数['坐标起点'], 横轴参数['坐标终点']
		衬底平面.set_xlim(横标起点, 横标终点)

		# 设置纵轴坐标范围
		纵标起点, 纵标终点= 0, 1
		衬底平面.set_ylim(纵标起点, 纵标终点)

		# 改变外框的颜色
		for 方位, 边框 in 衬底平面.spines.items():	# 方位: 'left' | 'right' | 'top' | 'bottom'
			边框.set_color(__color_gold__)

		# 不准显示坐标值
		for 主坐标 in 衬底平面.get_xticklabels(minor=False):
			主坐标.set_visible(False)
		for 副坐标 in 衬底平面.get_xticklabels(minor=True):
			副坐标.set_visible(False)
		for 主坐标 in 衬底平面.get_yticklabels(minor=False):
			主坐标.set_visible(False)
		for 副坐标 in 衬底平面.get_yticklabels(minor=True):
			副坐标.set_visible(False)

		# 不准显示 ticks
		衬底横轴= 衬底平面.get_xaxis()
		衬底纵轴= 衬底平面.get_yaxis()

		衬底横轴.set_ticks_position('none')
		衬底纵轴.set_ticks_position('none')

		#	画一小时整点标志线
		#============================================================================================================
		标注位置= 横轴参数['标注位置']
		衬底平面.plot((标注位置['09:30'], 标注位置['09:30']), (纵标起点, 纵标终点), '-', color='0.3', linewidth=0.9)
		衬底平面.plot((标注位置['10:30'], 标注位置['10:30']), (纵标起点, 纵标终点), '-', color='0.3', linewidth=0.9)
		衬底平面.plot((标注位置['11:30'], 标注位置['11:30']), (纵标起点, 纵标终点), '-', color='0.3', linewidth=0.9)
		衬底平面.plot((标注位置['13:00'], 标注位置['13:00']), (纵标起点, 纵标终点), '-', color='0.3', linewidth=0.9)
		衬底平面.plot((标注位置['14:00'], 标注位置['14:00']), (纵标起点, 纵标终点), '-', color='0.3', linewidth=0.9)
		衬底平面.plot((标注位置['15:00'], 标注位置['15:00']), (纵标起点, 纵标终点), '-', color='0.3', linewidth=0.9)

		# 画价格部分与成交部分的分割线
		分隔纵标= 手数子图高度 / 纵轴高度
		衬底平面.plot((横标起点, 横标终点), (分隔纵标, 分隔纵标), '-', color=__color_gold__, linewidth=1.0, alpha=1.0)

		# 保存
		self._衬底平面= 衬底平面

		#	子图初始化
		#=======================================================================================================
		子图偏移= (图系横移+0.0, 图系纵移+0.0)
		self._分时手数子图.平面初始化(图片对象=图片对象, 子图偏移=子图偏移, 全图大小=全图大小)

		sharex= self._分时手数子图.返回指数平面()
		子图偏移= (图系横移+0.0, 图系纵移+手数子图高度)
		self._分时价格子图.平面初始化(图片对象=图片对象, 子图偏移=子图偏移, 全图大小=全图大小, sharex=sharex)



	def 图系绘图(self):
		'''

		'''
		self._分时价格子图.绘图()
		self._分时手数子图.绘图()





class 文字信息区块:
	'''

	'''

	def __init__(self, parent, 绘图数据):
		'''

		'''
		self._parent= parent
		self._ilogger= parent._ilogger
		self._公司信息子图= 公司信息子图(parent=self, 绘图数据=绘图数据)



	def 返回区块大小(self):
		'''

		'''
		return self._公司信息子图.返回本图大小()



	def 区块平面初始化(self, 图片对象, 区块偏移, 全图大小):
		'''

		'''
		本区横移, \
		本区纵移= 区块偏移

		子图偏移= (本区横移+0.0, 本区纵移+0.0)
		self._公司信息子图.平面初始化(图片对象=图片对象, 子图偏移=子图偏移, 全图大小=全图大小)



	def 区块绘图(self):
		'''

		'''
		self._公司信息子图.绘图()





class 日线行情区块:
	
	def __init__(self, parent, 绘图数据):
		'''

		'''
		self._parent= parent
		self._ilogger= parent._ilogger
		self._日线价格子图= 日线价格子图(parent=self, 绘图数据=绘图数据)
		self._日线换手子图= 日线换手子图(parent=self, 绘图数据=绘图数据)

		self._顶部空白= 0.3 * __纵轴倍率__



	def 返回区块大小(self):
		'''

		'''
		顶部空白= self._顶部空白

		日线价格宽度, \
		日线价格高度= self._日线价格子图.返回本图大小()

		日线换手高度= self._日线换手子图.返回纵轴高度()

		横轴宽度= 日线价格宽度
		纵轴高度= 顶部空白 + 日线价格高度 + 日线换手高度

		return (横轴宽度, 纵轴高度)



	def 区块平面初始化(self, 图片对象, 区块偏移, 全图大小):
		'''

		'''
		本区横移, \
		本区纵移= 区块偏移

		日线换手高度= self._日线换手子图.返回纵轴高度()

		# 日线价格子图
		子图偏移= (本区横移+0.0, 本区纵移+日线换手高度)
		self._日线价格子图.平面初始化(图片对象=图片对象, 子图偏移=子图偏移, 全图大小=全图大小)

		# 日线换手子图
		sharex= self._日线价格子图.返回指数平面()
		子图偏移= (本区横移+0.0, 本区纵移+0.0)
		self._日线换手子图.平面初始化(图片对象=图片对象, 子图偏移=子图偏移, 全图大小=全图大小, sharex=sharex)



	def 区块绘图(self):
		'''

		'''
		self._日线价格子图.绘图()
		self._日线换手子图.绘图()





class 分时大图区块:
	'''
	区分大图区块和小图区块的目的是可以为分时行情（包括当日实盘行情）采用两种不同的缩放比
	'''

	def __init__(self, parent, 绘图数据):
		'''

		'''
		self._parent= parent
		self._ilogger= parent._ilogger

		self._顶部空白= 1.2 * __纵轴倍率__
		self._图系间隙= 3.0 * __横轴倍率__

		日线数据= 绘图数据['日线数据']
		分时数据= 绘图数据['分时数据']
		实盘数据= 绘图数据['实盘数据']
		任务参数= 绘图数据['任务参数']

		self._目标日期列表= sorted(分时数据.keys())
		self._分时图系集合= {日期 : 分时行情图系(parent=self, 目标日期=日期, 绘图数据=绘图数据) for 日期 in self._目标日期列表}

		#	如果需要，把 实盘日期日期加入 目标日期列表，实盘价格和手数子图 加入子图集合
		#==================================================================================================
		if 任务参数['绘制实盘']:
			实盘日期= 实盘数据['实盘日期']
			self._目标日期列表.append(实盘日期)
			self._分时图系集合[实盘日期]= 实盘行情图系(parent=self, 目标日期=实盘日期, 绘图数据=绘图数据)

		#	计算目标日期连续记录
		#==================================================================================================
		self._连续日期记录, \
		self._左侧连续记录= self.计算连续日期记录(日线数据=日线数据)

		# 计算连续目标日期段的纵轴坐标上下限
		纵标区间记录= {}	# key 是日期，value 是 dict，标示个股与指数纵标的最高、最低值
		成交步进记录= {}		# 与上类似，value 是 dict，标示个股与指数的步进值
		for 记录 in self._连续日期记录:
			# 计算价格子图纵标区间
			各自区间= [self._分时图系集合[日期].计算纵轴坐标区间() for 日期 in 记录]
			综合区间= {
				'个股最高': max( [rec['个股最高'] for rec in 各自区间] ),
				'个股最低': min( [rec['个股最低'] for rec in 各自区间] ),
				'指数最高': max( [rec['指数最高'] for rec in 各自区间] ),
				'指数最低': min( [rec['指数最低'] for rec in 各自区间] ),
			}
			# 计算手数子图步进值
			各自步进= [self._分时图系集合[日期].计算成交步进记录() for 日期 in 记录]
			综合步进= {
				'个股步进': max( [rec['个股步进'] for rec in 各自步进] ),
			}
			# 记录纵标区间与步进值
			for 日期 in 记录:
				纵标区间记录[日期]= 综合区间
				成交步进记录[日期]= 综合步进

		#	把子图纵轴区间记录交给下级分时价格子图，完成计算子图纵轴参数
		#==================================================================================================
		for 日期, 图系 in self._分时图系集合.items():
			图系.计算价格子图纵轴参数(坐标区间=纵标区间记录[日期] if 日期 in 纵标区间记录 else None)
			图系.计算手数子图纵轴参数(步进记录=成交步进记录[日期] if 日期 in 成交步进记录 else None)

		#	计算本区块的尺寸和下级图系的布局
		#==================================================================================================
		self._图系偏移记录, \
		self._区块横轴宽度= self.计算图系横轴余量()
		self._区块纵轴高度= max(图系.返回图系纵轴高度() for 图系 in self._分时图系集合.values()) + self._顶部空白



	def 计算图系横轴余量(self):
		'''

		'''

		偏移记录= {}
		当前偏移= 0.0
		for 偏移, 日期 in enumerate(self._目标日期列表):
			图系= self._分时图系集合[日期]
			if 偏移 > 0 and 日期 not in self._左侧连续记录:
				当前偏移 += self._图系间隙
			偏移记录[日期]= 当前偏移
			当前偏移 += 图系.返回图系横轴宽度()

		横轴宽度= 当前偏移
		return 偏移记录, 横轴宽度



	def 计算连续日期记录(self, 日线数据):
		'''

		'''
		连续日期记录= []
		左侧连续记录= []
		目标日期列表= self._目标日期列表
		目标日期个数= len(目标日期列表)
		if 目标日期个数 > 1:
			个股日期= 日线数据['个股日线']['日期']
			位置序列= [个股日期.index(日期) for 日期 in 目标日期列表]
			新建记录= set()
			for (前日偏移, 前日日期), (当日偏移, 当日日期) in zip(enumerate(目标日期列表[:-1]), enumerate(目标日期列表[1:], start=1)):
				if 位置序列[当日偏移] - 位置序列[前日偏移] == 1:	# 连续
					左侧连续记录.append(当日日期)
					新建记录.add(前日日期)
					新建记录.add(当日日期)
				elif 新建记录:		# 连续段已结束
					连续日期记录.append(tuple(sorted(新建记录)))
					新建记录= set()
			if 新建记录:	# 补上最后一个（如果存在）
				连续日期记录.append(tuple(sorted(新建记录)))
		return 连续日期记录, 左侧连续记录



	def 返回区块大小(self):
		'''

		'''
		return (self._区块横轴宽度, self._区块纵轴高度)



	def 区块平面初始化(self, 图片对象, 区块偏移, 全图大小):
		'''

		'''
		
		本区横移, \
		本区纵移= 区块偏移

		图系偏移记录= self._图系偏移记录

		# 下级图系平面初始化
		for 日期, 图系 in self._分时图系集合.items():
			图系偏移= (本区横移+图系偏移记录[日期], 本区纵移+0.0)
			图系.图系平面初始化(图片对象=图片对象, 图系偏移=图系偏移, 全图大小=全图大小)



	def 区块绘图(self):
		'''

		'''
		for 图系 in self._分时图系集合.values():
			图系.图系绘图()







class 分时小图区块:
	'''
	区分大图区块和小图区块的目的是可以为分时行情（包括当日实盘行情）采用两种不同的缩放比
	'''

	def __init__(self, parent, 绘图数据):
		'''

		'''
		self._parent= parent
		self._ilogger= parent._ilogger



	def 返回区块大小(self):
		'''

		'''
		return (0, 0)



	def 区块平面初始化(self, 图片对象, 区块偏移, 全图大小):
		'''

		'''
		pass



	def 区块绘图(self):
		'''

		'''
		pass





class MyFigure:
	'''

	'''
	def __init__(self, tname, ilogger, 绘图数据):
		'''

		'''
		self._tname= tname
		self._ilogger= ilogger

		#	图片相关数据
		#===============================================================================================================
		# 图片名称、目录
		self._图片名称= 绘图数据['图片名称']
		self._图片目录= 绘图数据['图片目录']
		self._图片路径= os.path.join(self._图片目录, self._图片名称)

		#	下级数据
		#===============================================================================================================
		self._任务参数= 绘图数据['任务参数']
		self._公司信息= 绘图数据['公司信息']
		self._日线数据= 绘图数据['日线数据']
		self._分时数据= 绘图数据['分时数据']
		self._实盘数据= 绘图数据['实盘数据']

		#	处理日线数据
		#===============================================================================================================
		self.处理日线数据()
		self.处理分时数据()

		#	建立下级区块对象
		#===============================================================================================================
		self._文字信息区块= 文字信息区块(parent=self, 绘图数据=绘图数据)
		self._日线行情区块= 日线行情区块(parent=self, 绘图数据=绘图数据)
		self._分时大图区块= 分时大图区块(parent=self, 绘图数据=绘图数据) if self._任务参数['绘制分时'] or self._任务参数['绘制实盘'] else None
		self._分时小图区块= 分时小图区块(parent=self, 绘图数据=绘图数据)

		#	计算全图大小
		#===============================================================================================================

		# 图形部件颜色、尺寸等基本配置
		self._facecolor= __color_pink__
		self._edgecolor= __color_navy__
		self._dpi= self._任务参数['dpi'] if 'dpi' in self._任务参数 else 300
		self._linewidth= 1.0

		self._左侧空白= 12.0 * __横轴倍率__
		self._右侧空白= 12.0 * __横轴倍率__
		self._顶部空白= 0.3  * __纵轴倍率__
		self._底部空白= 1.2  * __纵轴倍率__

		# 开始计算
		self._全图大小= self.计算全图大小()

		#	根据计算出的尺寸建立 Figure 对象
		#===============================================================================================================
		self._图片对象= pyplot.figure(
			figsize= self._全图大小,
			dpi= self._dpi,
			facecolor= self._facecolor,
			edgecolor= self._edgecolor,
			linewidth= self._linewidth )	# Figure 对象

		#	把图片对象交给下级完成下级子图的初始化
		#===============================================================================================================
		区块布局= self.计算区块布局()
		self._文字信息区块.区块平面初始化(图片对象=self._图片对象, 区块偏移=区块布局['文字信息区块'], 全图大小=self._全图大小)
		self._日线行情区块.区块平面初始化(图片对象=self._图片对象, 区块偏移=区块布局['日线行情区块'], 全图大小=self._全图大小)
		if self._分时大图区块: self._分时大图区块.区块平面初始化(图片对象=self._图片对象, 区块偏移=区块布局['分时大图区块'], 全图大小=self._全图大小)
		if self._分时小图区块: self._分时小图区块.区块平面初始化(图片对象=self._图片对象, 区块偏移=区块布局['分时小图区块'], 全图大小=self._全图大小)



	def 处理日线数据(self):
		'''

		'''
		任务参数= self._任务参数
		公司信息= self._公司信息
		日线数据= self._日线数据

		个股日线= 日线数据['个股日线']
		指数日线= 日线数据['指数日线']

		复权绘图= 任务参数['复权绘图']
		均线参数= 任务参数['个股均线参数']
		绘制均线= 任务参数['绘制个股均线']

		# TODO: 如果需要，把今日实盘数据加入个股行情以及指数行情
		if self._任务参数['绘制实盘']:
			pass

		# 计算个股换手率
		股本变更记录= 公司信息['股本变更记录']
		Public.计算个股换手率(个股行情=个股日线, 个股股本变更记录=股本变更记录)

		# 计算复权行情。XXX: 注意 复权日线 中是否含均线集取决于传递的 均线参数
		复权日线= Public.计算复权行情(个股行情=个股日线, 均线参数=(均线参数 if 绘制均线 else None))
		复权日线['换手率']= 个股日线['换手率']
		复权记录= 复权日线.pop('复权记录')

		日线数据['复权记录']= 复权记录
		if 绘制均线:
			复权均线= 复权日线.pop('均线集')

		# 计算绘图用的补全行情
		绘图行情= {}

		绘图日线= copy.deepcopy(复权日线 if 复权绘图 else 个股日线)
		绘图行情.update(绘图日线)

		if 绘制均线:	# 计算绘图用的个股均线（是否复权由任务参数控制）
			if 复权绘图:
				绘图均线= copy.deepcopy(复权均线)
			else:
				开盘= 个股日线['开盘']
				最高= 个股日线['最高']
				收盘= 个股日线['收盘']
				最低= 个股日线['最低']
				绘图均线= { n : Public.计算序列加权均线(开盘, 最高, 收盘, 最低, n) for n in 均线参数 }
			绘图行情.update(绘图均线)

		Public.补全个股行情(完整日期=指数日线['日期'], 个股行情=绘图行情)

		日线数据['绘图日线']= 绘图日线
		if 绘制均线:
			日线数据['绘图均线']= 绘图均线

		# 计算个股衍生行情。这里不用 deepcopy() 了
		衍生行情= 复权日线	# XXX: 注意: 复权日线 内可能包含 均线集
		if 绘制均线:
			衍生行情['均线集']= 复权均线
		Public.计算个股行情衍生数据(ilogger=self._ilogger, 个股行情=衍生行情, 均线参数=None)	# 这里不用传递 均线参数，衍生行情 里已经包含均线集。

		日线数据['个股衍生行情']= 衍生行情



	def 处理分时数据(self):
		'''
		把 日线行情 中的数据添加到 分时行情 当中
		'''
		任务参数= self._任务参数
		#	公司信息= self._公司信息
		日线数据= self._日线数据
		分时数据= self._分时数据

		# 处理个股分时数据
		个股量均参数= 任务参数['个股量均参数']
		指数量均参数= 任务参数['指数量均参数']

		个股日线= 日线数据['个股日线']
		个股日期= 个股日线['日期']
		个股开盘= 个股日线['开盘']
		个股最高= 个股日线['最高']
		个股收盘= 个股日线['收盘']
		个股最低= 个股日线['最低']
		个股成交量= 个股日线['成交量']

		指数日线= 日线数据['指数日线']
		指数日期= 指数日线['日期']
		指数开盘= 指数日线['开盘']
		指数最高= 指数日线['最高']
		指数收盘= 指数日线['收盘']
		指数最低= 指数日线['最低']
		指数成交量= 指数日线['成交量']

		时刻常数= {
			'上午开始' : datetime.time(hour=9,  minute=25, second=0 ),	# 如果是实盘，设成 9:30
			'上午结束' : datetime.time(hour=11, minute=30, second=10),
			'下午开始' : datetime.time(hour=12, minute=59, second=50),
			'下午结束' : datetime.time(hour=15, minute=0,  second=30),
			'12:00:00' : datetime.time(hour=12, minute=0,  second=0 ),	# 把任意时间转化成坐标的时候要用到
			'09:25:00' : datetime.time(hour=9,  minute=25, second=0 ),
			'09:30:00' : datetime.time(hour=9,  minute=30, second=0 ),
			'13:00:00' : datetime.time(hour=13, minute=0,  second=0 ),
		}

		for 日期, 分时 in 分时数据.items():
			#	时间常数
			#========================================================================================
			日期对象= 分时['日期对象']
			时间常数= {key : datetime.datetime.combine(日期对象, val) for key, val in 时刻常数.items()}
			分时['时间常数']= 时间常数

			#	添加日线相关数据
			#========================================================================================
			index= 个股日期.index(日期)
			分时['个股当日开盘']= 个股开盘[index]
			分时['个股当日最高']= 个股最高[index]
			分时['个股前日收盘']= 个股收盘[index-1] if index>0 else None
			分时['个股当日最低']= 个股最低[index]

			# 计算前期平均手数 XXX: 如果以后 日线数据 中增加了成交量均线，那么这部分数据可以直接从中截取。
			分时['个股平均成交']= {Public.计算均值(个股成交量[-n:]) for n in 个股量均参数}	# 结果: (均值, 最大值, 最小值, 标准差, 长度)

			index= 指数日期.index(日期)
			分时['指数当日开盘']= 指数开盘[index]
			分时['指数当日最高']= 指数最高[index]
			分时['指数前日收盘']= 指数收盘[index-1] if index>0 else None
			分时['指数当日最低']= 指数最低[index]

			# 计算前期平均手数 XXX: 如果以后 日线数据 中增加了成交量均线，那么这部分数据可以直接从中截取。
			分时['指数平均成交']= {Public.计算均值(指数成交量[-n:]) for n in 指数量均参数}	# 结果: (均值, 最大值, 最小值, 标准差, 长度)

			#	修改分时数据，截掉边界外的部分（主要是为了与未来的指数行情统一）
			#========================================================================================
			#	if 分时['个股行情有效']:
			#		行情= 分时['个股分时行情']
			#		时间序列= 行情['时间序列']
			#		价格序列= 行情['价格序列']
			#		手数序列= 行情['手数序列']
			#		金额序列= 行情['金额序列']
			#		备注序列= 行情['备注序列']

			#		分时序列= [
			#			(时间, 价格, 手数, 金额, 备注) \
			#			for 时间, 价格, 手数, 金额, 备注 in zip(时间序列, 价格序列, 手数序列, 金额序列, 备注序列) \
			#			if (时间>=时间常数['上午开始'] and 时间<=时间常数['上午结束']) or (时间>=时间常数['下午开始'] and 时间<=时间常数['下午结束'])
			#		]

			#		行情['时间序列'], \
			#		行情['价格序列'], \
			#		行情['手数序列'], \
			#		行情['金额序列'], \
			#		行情['备注序列']= zip(*分时序列)

			#		#	价格序列= 行情['价格序列']
			#		#	行情['上涨标记']= [False] + [True if p2>p1  else False for p1, p2 in zip(价格序列[:-1], 价格序列[1:])]
			#		#	行情['下跌标记']= [False] + [True if p2<p1  else False for p1, p2 in zip(价格序列[:-1], 价格序列[1:])]
			#		#	行情['平盘标记']= [True]  + [True if p2==p1 else False for p1, p2 in zip(价格序列[:-1], 价格序列[1:])]

		# TODO: 修改 指数分时 数据 ... ...



	def 计算全图大小(self):
		'''

		'''
		左侧空白= self._左侧空白
		右侧空白= self._右侧空白
		顶部空白= self._顶部空白
		底部空白= self._底部空白

		文字信息宽度, 文字信息高度= self._文字信息区块.返回区块大小()
		日线行情宽度, 日线行情高度= self._日线行情区块.返回区块大小()
		分时大图宽度, 分时大图高度= self._分时大图区块.返回区块大小() if self._分时大图区块 else (0, 0)
		分时小图宽度, 分时小图高度= self._分时小图区块.返回区块大小() if self._分时小图区块 else (0, 0)

		横轴宽度= 左侧空白 + max(文字信息宽度, 日线行情宽度, 分时大图宽度, 分时小图宽度) + 右侧空白
		纵轴高度= 顶部空白 + 文字信息高度 + 日线行情高度 + 分时大图高度 + 分时小图高度 + 底部空白

		return (横轴宽度, 纵轴高度)



	def 计算区块布局(self):
		'''

		'''
		左侧空白= self._左侧空白
		右侧空白= self._右侧空白
		顶部空白= self._顶部空白
		底部空白= self._底部空白

		全图宽度, \
		全图高度= self._全图大小

		文字信息宽度, 文字信息高度= self._文字信息区块.返回区块大小()
		日线行情宽度, 日线行情高度= self._日线行情区块.返回区块大小()
		分时大图宽度, 分时大图高度= self._分时大图区块.返回区块大小() if self._分时大图区块 else (0, 0)
		分时小图宽度, 分时小图高度= self._分时小图区块.返回区块大小() if self._分时小图区块 else (0, 0)

		区块布局= {
			'文字信息区块': (左侧空白+(全图宽度-左侧空白-右侧空白-文字信息宽度)/2 , 底部空白+分时小图高度+分时大图高度+日线行情高度),
			'日线行情区块': (左侧空白+(全图宽度-左侧空白-右侧空白-日线行情宽度)/2 , 底部空白+分时小图高度+分时大图高度),
			'分时大图区块': (左侧空白+(全图宽度-左侧空白-右侧空白-分时大图宽度)/2 , 底部空白+分时小图高度) if self._分时大图区块 else None,
			'分时小图区块': (左侧空白+(全图宽度-左侧空白-右侧空白-分时小图宽度)/2 , 底部空白) if self._分时小图区块 else None,
		}

		return 区块布局



	def 绘图并保存(self):
		'''

		'''
		self._文字信息区块.区块绘图()
		self._日线行情区块.区块绘图()
		if self._分时大图区块: self._分时大图区块.区块绘图()
		if self._分时小图区块: self._分时小图区块.区块绘图()

		self._图片对象.savefig( \
			self._图片路径, \
			dpi=self._dpi, \
			facecolor=self._facecolor, \
			edgecolor=self._edgecolor, \
			linewidth=self._linewidth \
		)



if __name__ == '__main__':

	程序目录= os.getcwd()

	pfile= open(file=os.path.join(程序目录, '绘图数据.pickle'), mode='rb')
	绘图数据= pickle.load(pfile)
	pfile.close()

	绘图数据['图片目录']= 程序目录
	绘图数据['图片名称']= '000553_沙隆达Ａ_2012-01-04~2013-04-19.png'

	tname= 绘图数据['图片名称']
	ilogger= Public.TempLogger(loggername='绘图脚本_'+tname, filename='绘图.log', taskdir=程序目录)

	输出= '绘图数据:\n\n'
	输出 += Public.repr_data(data=绘图数据)
	ilogger.debug(输出)

	# 如果需要，import 用户定制绘图函数
	任务参数= 绘图数据['任务参数']
	if '定制绘图函数' in 任务参数 and 任务参数['定制绘图函数']:
		用户目录= 任务参数['定制绘图函数']['用户目录']
		组件名称= 任务参数['定制绘图函数']['组件名称']
		函数名称= 任务参数['定制绘图函数']['函数名称']
		函数参数= 任务参数['定制绘图函数']['函数参数']
		sys.path.append(用户目录)
		用户组件= __import__(组件名称, globals(), locals(), [函数名称], 0)
		sys.path.remove(用户目录)
		任务参数['定制绘图参数']= 函数参数
		任务参数['定制绘图函数']= 用户组件.__dict__[函数名称]
	else:
		任务参数['定制绘图参数']= None
		任务参数['定制绘图函数']= None

	print('绘图中 ...')
	myfigure= MyFigure(tname=tname, ilogger=ilogger, 绘图数据=绘图数据)
	myfigure.绘图并保存()
	print('好了。请使用 Vim 浏览和编辑 log 文件与源文件。')















