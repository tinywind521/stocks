import math

from functions import getValue


class Stock:
    """
    stock 类的测试版
    code: 代码
    ref_list: 包含timetype、beginDay、appcode等在内其他参数字典
    开发者：Q0233
    最后更新：未完成
    注意：分时数据是逆序，K线数据是顺序。
    """
    def __init__(self, code, ref_List):
        if ref_List is None:
            ref_List = {'KtimeType': '60/day',
                        'KbeginDay': '20170101',
                        'KgetLength': 10,
                        'TdayLength': 5,
                        'TgetLength': 1,
                        'appcode': 'c7689f18e1484e9faec07122cc0b5f9e'}
        self.code = code
        self._ref_list = ref_List
        self.Kvalue = None
        self.Tvalue = None
        # self.value = self.get_KValue()
        self.Kstatus = {'涨幅': '', '开收': '', '量能': '', '上针': '', '下针': '',
                        '布林': '', '轨距': '', '层级': '', '趋势': '',
                        '平台': '', '预留': '', '备用': ''}


    def get_ref_List(self):
        return self._ref_list


    """
    无情的分割线
    下面是获取基本K线的函数方法
    """
    def _get_KLine(self):
        """
        获取各级别的K线
        :return: Error return None
        """
        try:
            if self._ref_list['KtimeType'] == '60':
                self.Kvalue = getValue.get_60F(self.code, self._ref_list['KbeginDay'],
                                               self._ref_list['KgetLength'])
            elif self._ref_list['KtimeType'] == 'day':
                self.Kvalue = getValue.get_dayK(self.code, self._ref_list['KbeginDay'],
                                                self._ref_list['KgetLength'])
        except ValueError:
            self.Kvalue = None


    def get_KValue(self):
        """
        该函数作用便于多次读取K线数据
        但不需要多次联网
        :return:
        """
        if self.Kvalue is None:
            # print('Link Web!')
            self._get_KLine()
            return self.Kvalue
        else:
            return self.Kvalue


    def set_KbeginDay(self, KbeginDay='20170101'):
        self._ref_list['KbeginDay'] = KbeginDay


    def set_KtimeType(self, Ktimetype='60'):
        self._ref_list['KtimeType'] = Ktimetype


    def set_KgetLength(self, KgetLength=10):
        self._ref_list['KgetLength'] = KgetLength


    def get_KbeginDay(self):
        return self._ref_list['KbeginDay']


    def get_KtimeType(self):
        return self._ref_list['KtimeType']


    def get_KgetLength(self):
        return self._ref_list['KgetLength']


    def set_KClear(self):
        """
        清空K线序列
        :return:
        """
        self.Kvalue = None
        self.Kstatus = None


    def set_KRefresh(self):
        """
        刷新K线序列
        :return:
        """
        self.set_KClear()
        self.get_KValue()


    """
    无情的分割线
    下面是分时的函数方法
    """
    def _get_TLine(self):
        """
        获取分时线
        :return: Error return None
        """
        try:
            self.Tvalue = getValue.get_timeLine(self.code,
                                                self._ref_list['TdayLength'])
        except ValueError:
            self.Tvalue = None


    def get_TValue(self):
        """
        该函数作用便于多次读取分时数据
        但不需要多次联网
        :return:
        """
        if self.Tvalue is None:
            self._get_TLine()
            # print(self._ref_list)
            self.Tvalue = self.Tvalue[0: self._ref_list['TgetLength']]
            return self.Tvalue
        else:
            if len(self.Tvalue) < self._ref_list['TgetLength']:
                self._get_TLine()
                self.Tvalue = self.Tvalue[0: self._ref_list['TgetLength']]
            else:
                self.Tvalue = self.Tvalue[0: self._ref_list['TgetLength']]
            return self.Tvalue


    def set_TdayLength(self, TdayLength=5):
        self._ref_list['TdayLength'] = TdayLength


    def set_TgetLength(self, TgetLength=1):
        if TgetLength > self._ref_list['TdayLength']:
            self._ref_list['TdayLength'] = self._ref_list['TdayLength']
        else:
            self._ref_list['TgetLength'] = TgetLength


    def get_TdayLength(self):
        return self._ref_list['TdayLength']


    def get_TgetLength(self):
        return self._ref_list['TgetLength']


    def set_TClear(self):
        """
        清空分时序列
        :return:
        """
        self.Tvalue = None


    def set_TRefresh(self):
        """
        刷新分时序列
        :return:
        """
        self.set_TClear()
        self.get_TValue()


    """
    无情的分割线
    下面是布林的函数方法
    """
    def boll_mid(self, n=0):
        """
        直接获得K线Boll数据
        :return:
        """
        if self.Kvalue is None:
            self._get_KLine()
        bollmid = self.Kvalue[-1-n]['mid']
        return bollmid


    def boll_upper(self, n=0):
        """
        直接获得K线Boll数据
        :return:
        """
        if self.Kvalue is None:
            self._get_KLine()
        bollupper = self.Kvalue[-1-n]['upper']
        return bollupper


    def boll_lower(self, n=0):
        """
        直接获得K线Boll数据
        :return:
        """
        if self.Kvalue is None:
            self._get_KLine()
        bolllower = self.Kvalue[-1-n]['lower']
        return bolllower


    """
    华丽的分割线
    下面是获取K线参数的函数方法
    """
    def update_Kstatus(self):
        if self.Kvalue:
            # print(self.Kvalue)
            i = 0
            for _Kvalue in self.Kvalue:
                # print(_Kvalue)
                self.update_K参数(_Kvalue)
                _Kvalue.update(self.Kstatus)
                self.Kvalue[i] = _Kvalue
                i += 1


    # def clear_Kstatus(self):
    #     self.Kstatus = None


    def update_K参数(self, _Kvalue):
        """
        按照K线的涨幅、开盘收盘涨幅、收针判断、布林位置、结合收针的量能 归类 量化
        zf：涨幅
        ks：收盘对应开盘的涨幅（基准昨收）
        sz：上针幅度（基准为振幅）
        xz：下针幅度（基准为振幅）

        :return:
        """
        try:
            if round(_Kvalue['lastclose'] * 1.1, 2) == _Kvalue['close']:
                zf = 10
            elif round(_Kvalue['lastclose'] * 0.9, 2) == _Kvalue['close']:
                zf = -10
            else:
                zf = 100.0000 * (_Kvalue['close'] - _Kvalue['lastclose']) / _Kvalue['lastclose']
            ks = 100.0000 * (_Kvalue['close'] - _Kvalue['open'] + 0.001) / _Kvalue['lastclose']
        except ZeroDivisionError:
            self.Kstatus['涨幅'] = 0
            self.Kstatus['开收'] = 0
            self.Kstatus['上针'] = 0
            self.Kstatus['下针'] = 0
        else:
            self.Kstatus['涨幅'] = math.floor(zf)
            self.Kstatus['开收'] = math.floor(ks)
            try:
                high = max(_Kvalue['open'], _Kvalue['close'])
                low = min(_Kvalue['open'], _Kvalue['close'])
                full = _Kvalue['max'] - _Kvalue['min']
                sz = 100.0000 * (_Kvalue['max'] - high) / full
                xz = 100.0000 * (low - _Kvalue['min']) / full
            except ZeroDivisionError:
                self.Kstatus['上针'] = 0
                self.Kstatus['下针'] = 0
            else:
                self.Kstatus['上针'] = math.floor(sz)
                self.Kstatus['下针'] = math.floor(xz)
