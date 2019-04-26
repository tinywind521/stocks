from multiprocessing.dummy import Pool as ThreadPool
from Dino.DataSource.httpAPI import DataSourceQQ as QQ
from Dino.DataSource.httpAPI import DailyQQMul as QQMul
from Dino.DataSource.httpAPI import DataTuShare as Tu

import time
import sys

def getCodeListAndColList():
    value = {'codeList':[], 'colList':[]}
    data = Tu()
    codeList = data.getList()
    print('List get!')
    data.setCode(codeList[0])
    data.getDailyKLine()
    data.updateDailyKLine()
    colList = data.colList
    value['codeList'] = codeList
    value['colList'] = colList
    return value

def view_bar(num, total, codeIn=''):
    rate = num / total
    rate_num = rate * 100
    flow = int(rate_num)
    r = ('\r[%s%s] %2.2f%% %d/%d %s' % ("|"*flow, " "*(100-flow), rate_num, num, total, codeIn,)) + \
        str(time.strftime("%H:%M:%S", time.localtime()))
    sys.stdout.write(r)
    sys.stdout.flush()

"""
Daily分析处理
"""
def dailyFilter(temp):
    code = temp['code']
    dailyKline = dailySingleDataCapture(code)
    filter_LimitInDays(code, dailyKline)

def filter_LimitInDays(code, dailyKline, dayLength=40):
    temp = dailyKline[:dayLength]
    result = temp[temp.limit ==1]
    if not result.empty:
        result.to_csv('d:/data/' + code + '.csv')
    return None

def dailySingleDataCapture(code):
    """
    多线程处理
    DataTuShareMul
    :param temp codeList = [{'code': k} for k in realList]
    :return:
    """
    # print(code)
    data = QQMul(code)
    sleepTime = 10
    # obj.updateDailyKLine(colList, code)
    while True:
        try:
            data.updateDailyKLine()
            # data.updateDailyKLineDB()
            break
        except ValueError:
            print(code, 'time sleep...')
            time.sleep(sleepTime)
    return data.dailyKline


class StockFilter:
    """
    筛选过滤器
    """
    def __init__(self, codeList, colList=None):
        self.codeList = codeList
        self.colList = colList
        self.code = None
        """
        多线程设定
        """
        self.poolLength = 20
        # self.qq = QQ(self.code)
        pass
        # self.code = code

    def getDailyDataMul(self):
        length = len(self.codeList)
        for i in range(0, length, self.poolLength):
            realList = self.codeList[i:i + self.poolLength]
            # print(realList)
            realLength = len(realList)
            view_bar(i + realLength, length)
            pool = ThreadPool(realLength)
            # objTemp = [{'code': k, 'colList': self.colList, 'obj': self.obj} for k in realList]
            codeList = [{'code': k} for k in realList]
            # print(objTemp)
            pool.map(dailyFilter, codeList)
            pool.close()
            pool.join()

    def getDailyData(self):
        pass


if __name__ == '__main__':
    debug = 0
    value = getCodeListAndColList()
    # print(value['codeList'])
    print(time.strftime("%H:%M:%S", time.localtime()))
    data = StockFilter(value['codeList'])
    data.getDailyDataMul()
    print(time.strftime("%H:%M:%S", time.localtime()))