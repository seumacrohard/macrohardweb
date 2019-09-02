'''
mhHot.py
提供类 mhHot
热销商品推荐
by 陶一丁 2019/8/28
'''

from MhDatabses import MhDatabases
from datetime import datetime
import operator
import pprint

# 类 mhHot
# 热销商品
# by 陶一丁 2019/8/28 
class mhHot:

# 函数 getPcr()
# 连接数据库，获取所有商品销售记录
# 返回二维字典
# by 陶一丁 2019/8/28 
	def getPcr(self):
	    db = MhDatabases()
	    result = db.executeQuery("select * from pcr")
	    return result;

# 函数 hot(result, n)
# 返回当月销量最多n件商品（降序）
# by 陶一丁 2019/8/28 
	def hot(self, result, n):
		data = {}
		hot = {}
		now = datetime.now()
		year = str(now.strftime('%Y'))
		month = str(now.strftime('%m'))
		for line in result:
			item = line[2]
			number = line[5]
			time = line[8].split('/')
			optype = line[10]
			data.setdefault(item,0)
			if item in data:
				if time[0]==year and time[1] == month and optype == 10:
					data[item] += number
			else:
				if time[0]==year and time[1] == month and optype == 10:
					data[item] = number			

		hot = sorted(data.items(), key = operator.itemgetter(1),reverse = True)[0:n]
		pprint.pprint(hot)
		return hot
'''
if __name__ == '__main__':
	h = mhHot()
	hot = h.hot(h.getPcr(), 3)
'''