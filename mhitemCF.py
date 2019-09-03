'''
mhitemCF.py modified from ItemCF.py
提供类 mhitemCF 
基于物品的协同过滤
by 陶一丁 2019/8/28
'''
from MhDatabses import MhDatabases 
from math import sqrt
import operator
import pprint

# 类 mhitemCF
# 基于物品的协同过滤
# by 陶一丁 2019/8/28 
class mhitemCF:

	# 函数 getPcr()
	# 连接数据库，获取所有商品销售记录
	# 返回二维字典
	# by 陶一丁 2019/8/28 
	def getPcr(self):
	    db = MhDatabases()
	    result = db.executeQuery("select * from pcr")
	    return result;

	# 函数 getUidScoreBid():
	# 计算用户对各个商品的兴趣度，对用户-商品进行倒排
	# 返回二维字典格式： {‘用户名’：{‘商品名称’：兴趣度}}
	# by 陶一丁 2019/8/28 
	def getUidScoreBid(self):
	    result = self.getPcr()
	    data ={};

	    for line in result:    
	        user = line[8];
	        item = line[2];
	        optype = line[9];
	        data.setdefault(user,{});
	        if item in data[user]:
	        	data[user][item] += optype; 
	        else: data[user][item] = optype;

	    print("----1.用户：物品的倒排----")
	    pprint.pprint(data) #pprint()让字典分行输出
	    print('\n')
	    return data       


	# 函数 similarity(data)
	# 构造物品-物品的共现矩阵
	# 计算物品与物品的相似矩阵
	# 输入：similarity(data) 输出的物品-物品相似矩阵（二维字典）
	# 输出： 物品-物品相似矩阵（二维字典）
	def similarity(self, data):
	    # 构造物品：物品的共现矩阵
	    N={};# 喜欢物品i的总人数
	    C={};# 喜欢物品i也喜欢物品j的人数
	    for user,item in data.items():
	        for i,score in item.items():
	            N.setdefault(i,0);
	            N[i]+=1;
	            C.setdefault(i,{});
	            for j,scores in item.items():
	                if j not in i:
	                    C[i].setdefault(j,0);
	                    C[i][j]+=1;

	    print("---2.构造的共现矩阵---")
	    print('N:',N)
	    print('C',C)
	    print('\n')

	    # 计算物品与物品的相似矩阵
	    W={};
	    for i,item in C.items():
	        W.setdefault(i,{});
	        for j,item2 in item.items():
	            W[i].setdefault(j,0);
	            W[i][j]=C[i][j]/sqrt(N[i]*N[j]);
	    print("---3.构造的相似矩阵---")
	    pprint.pprint(W)
	    print('\n')
	    return W   

	# 函数 recommandList(data,W,user,k=3,N=10)
	# 根据用户的历史记录，给用户推荐物品
	# 输入：data 为 getUidScoreBid() 输出的二维字典
	#       W 为 similarity(data) 输出的物品-物品相似矩阵（二维字典）
	#       user 为 string
	#       k 为 物品相似物品数
	#       N 为 推荐的最大商品数量
	# 输出：推荐的二维字典
	def recommandList(self, data,W,user,k=3,N=10):
	    rank={};
	    for i,score in data[user].items():# 获得用户user历史记录，如A用户的历史记录为{'a': '1', 'b': '1', 'd': '1'}
	        for j,w in sorted(W[i].items(),key=operator.itemgetter(1),reverse=True)[0:k]:#获得与物品i相似的k个物品
	            rank.setdefault(j,0);
	            rank[j]+=float(score) * w;

	    print("---4.推荐----")
	    pprint.pprint(sorted(rank.items(),key=operator.itemgetter(1),reverse=True)[0:N])
	    return sorted(rank.items(),key=operator.itemgetter(1),reverse=True)[0:N];


if __name__=='__main__':
	mh = mhitemCF()
	data = mh.getUidScoreBid() # 获得数据
	W = mh.similarity(data); # 算物品相似矩阵
	mh.recommandList(data,W,'18851662029',10,10); # 推荐
