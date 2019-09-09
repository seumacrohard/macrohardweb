import time
from functools import wraps

from flask import Flask, render_template, request, session, redirect, url_for, json

from MhDatabses import MhDatabases
from mhHot import mhHot
from mhitemCF import mhitemCF

app = Flask(__name__)

app.secret_key = 'test' # 设置secret_key


# 函数login_required
# 作用：管理员登录验证
# 作者：王明
# 完成时间：2019/08/22
def login_required(func):
    @wraps(func) # 修饰内层函数，防止当前装饰器去修改被装饰函数的属性
    def inner(*args, **kwargs):
        # 从session获取用户信息，如果有，则用户已登录，否则没有登录
        user_id = session.get('user_id')
        print("session user_id:", user_id)
        names = ["tyd", "wm", "wyh", "tlx", "wt"]
        y = 0
        for i in names:
            if i == user_id:
                y = 1
                break
        if y==0:
            return redirect('login')
        return func(*args, **kwargs)

    return inner

# 函数start
# 作用：管理员最开始的界面，介绍团队和项目
# 作者：王明
# 完成时间：2019/09/6
@app.route('/')
def start():
    return render_template("start.html")

# 函数login
# 作用：管理员登录路由函数，验证管理员账户密码是否正确
# 作者：王明
# 完成时间：2019/08/22
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 返回登录界面
    if request.method == 'GET':
        return render_template("login.html")
    else:
        # 获取用户名和密码
        name = request.form.get("username")
        pwd = request.form.get("password")
        session['user_id'] = name
        print("username:", name)
        print("password:", pwd)

        #设置内置管理员账户密码
        names = ["tyd", "wm", "wyh", "tlx", "wt"]
        pwds = ["tyd123", "wm123", "wyh123", "tlx123", "wt123"]

        # 验证是否是管理员账户密码，如果是，就登录进主界面，否则返回登录界面
        y = 0
        for i in names:
            if i == name and pwd == pwds[names.index(i)]:
                y = 1
                break
        if y == 1:
            return render_template("index.html")
        else:
            tip=1
            return render_template("login.html",tip=tip)


# 函数billList
# 作用：管理员页面账单管理路由函数，从数据库获取所有账单记录并显示在页面上，实现账单查询功能
# 作者：王明
# 完成时间：2019/08/23
@app.route('/billList', methods=['GET', 'POST'])
@login_required
def billList():
    db = MhDatabases()
    if request.method == 'GET':

        result = db.executeQuery("select image,gid,name ,sort,uprice,sum(number),sum(cast(total as decimal(18,1))) from pcr group by name") # 从数据库中查询账单记录并返回
        return render_template("billList.html",result=result)
    else:

        product = request.form.get("product") # 从web获取管理员输入的商品ID或者名称
        print(product)

        # 从数据库中查询获取账单记录
        result1 = db.executeQuery("select image,gid,name ,sort,uprice,sum(number),sum(cast(total as decimal(18,1))) from pcr where gid=%s group by name", [product])
        result2 = db.executeQuery("select image,gid,name ,sort,uprice,sum(number),sum(cast(total as decimal(18,1))) from pcr where name=%s group by name", [product])

        if len(result1)!=0 :
            result=result1
        elif len(result2)!=0 :
            result=result2
        else:
            result="暂无记录"
        return render_template("billList.html",result=result)


# 函数product
# 作用：管理员页面商品管理路由函数，从数据库获取所有商品信息并显示在页面上，实现商品查询，修改查看功能
# 作者：王明
# 完成时间：2019/08/23
@app.route('/product', methods=['GET', 'POST'])
@login_required
def product():
    db = MhDatabases()
    if request.method == 'GET':
        result = db.executeQuery("select * from goods") # 从数据库中查询商品记录并返回
        return render_template("product.html",result=result)
    else:

        proID=request.form.get("proid") # 获取web端发送的需要查询的商品ID
        print("proID",proID)
        pid=request.form.get("pid") # 获取web端发送的需要修改/查看的商品ID
        print("pid",pid)
        outofdate = request.form.get("outofdate")  # 获取web端发送的需要修改/查看的商品ID

        if outofdate=="search":
            todaydate=time.strftime("%Y-%m-%d")
            res=db.executeQuery("select * from goods")
            result=[]
            for i in res:
                if todaydate>i[7]:
                    result.append(i)
            return render_template("product.html", result=result)

        if proID:
            result1 = db.executeQuery("select * from goods where gid=%s",[proID]) # 从数据库获取查询的商品信息并返回
            result2 = db.executeQuery("select * from goods where name=%s", [proID])
            if len(result1) != 0:
                result = result1
            elif len(result2) != 0:
                result = result2
            else:
                result = "暂无记录"
            return render_template("product.html",result=result)
        if pid :
            return redirect(url_for('update',pid=pid)) # 跳转到商品修改界面

# 函数add
# 作用：管理员页面商品添加路由函数，实现添加新商品信息到数据库功能
# 作者：王明
# 完成时间：2019/08/23
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    db = MhDatabases()
    if request.method == 'GET':
        return render_template("add.html")
    else:
        # 获取web前端发送要添加的商品信息
        img=request.files.get("myFile")
        fname=img.filename
        filepath="./static/img/"+fname
        img.save("C:/macrohardweb/static/img/" + fname)
        product=[]
        product.append(request.form.get("productId"))
        product.append(request.form.get("productName"))
        product.append(filepath)
        product.append(request.form.get("type"))
        product.append(int(request.form.get("number")))
        product.append(float(request.form.get("price")))
        product.append(request.form.get("dateofproduce"))
        product.append(request.form.get("dateofbad"))
        product.append(request.form.get("location"))
        print(product)

        # 查询数据库中是否已存在该商品，如果不存在则向数据库添加商品信息
        result1 = db.executeQuery("select * from goods where gid=%s", [product[0]])
        result2 = db.executeQuery("select * from goods where name=%s",[product[1]])
        result3 = db.executeQuery("select * from goods where image=%s",[product[2]])
        if len(result1) == 0 and len(result2) == 0 and len(result3)==0:
            result = db.executeUpdate("insert into goods values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",product)
        else:
            result = 0
        return render_template("add.html",data=result)

# 函数update
# 作用：管理员页面商品修改路由函数，实现修改数据库中商品信息
# 作者：王明
# 完成时间：2019/08/23
@app.route('/update?<string:pid>', methods=['GET', 'POST'])
@login_required
def update(pid):
    db = MhDatabases()
    if request.method == 'GET':

        result = db.executeQuery("select * from goods where gid=%s",[pid]) # 从数据库获取商品信息并返回
        return render_template("update.html",result=result)
    else:
        gid=request.form.get("productId") # 获取web前端发送的要删除的商品ID
        print(gid)
        if gid:
            db.executeUpdate("delete from goods where gid=%s",[gid]) # 在数据库中删除商品信息
            return redirect(url_for('product'))
        else:
            # 获取web前端发送的商品要修改的信息
            product = []
            product.append(request.form.get("type"))
            product.append(int(request.form.get("number")))
            product.append(float(request.form.get("price")))
            product.append(request.form.get("location"))
            print(product)

            # 在数据库中修改商品信息
            db.executeUpdate("update goods set sort=%s,number=%s,uprice=%s,location=%s where gid=%s",[product[0],product[1],product[2],product[3],pid])
            return redirect(url_for('product'))

# 函数showEcharts
# 作用：向管理员web发送从数据库获取的商品销售总额
# 作者：王明
# 完成时间：2019/08/27
@app.route("/showEcharts",methods=["GET","POST"])
@login_required
def showEcharts():
    db = MhDatabases()
    #从数据库中查询数据---生成Json格式
    result=db.executeQuery("select sort,sum(cast(total as decimal(18,1))) from pcr group by sort ")
    sorts=[]
    for i in result:
        sorts.append(i[0])
    list1=[]
    for i in sorts:
        r=db.executeQuery("select name,sum(number) from pcr where sort=%s group by name ",[i])
        allgoods=[]
        for j in r:
            goods={}
            goods["name"]=j[0]
            goods["number"]=int(j[1])
            allgoods.append(goods)
        list1.append(allgoods)
    list2 =[]
    for i in result:
        dict ={}
        dict["sort"]=i[0]
        dict["total"]=float(i[1])
        list2.append(dict)
    res = {"result":list2,"goodsresult":list1}
    content = json.dumps(res)
    return content


# 函数showEchart
# 作用：管理员页面查看图表路由函数，获取商品和销售总额并以柱状图展示
# 作者：王明
# 完成时间：2019/08/27
@app.route("/showEchart")
@login_required
def showEchart():
    return  render_template("echarts.html")


# 函数userregister
# 作用：微信小程序用户注册路由，获取用户注册信息，判断是否存在后存入数据库
# 作者：王明
# 完成时间：2019/08/28
@app.route('/userregister',methods=['GET','POST'])
def userregister():
    db = MhDatabases()
    # 获取微信小程序端传来的注册用户的id，password，name，sex
    id = str(json.loads(request.values.get("id")))
    password=str(json.loads(request.values.get("password")))
    name = str(json.loads(request.values.get("name")))
    sex = str(json.loads(request.values.get("sex")))
    print("name",name," sex",sex," id",id," password",password)

    # 判断id是否已注册，将信息存入数据库
    result1=db.executeQuery("select * from user where phone=%s",[id])
    if len(result1) == 0:
        result = db.executeUpdate("insert into user values(%s,%s,%s,%s)", [id,password,sex,name])
        res = "注册成功"
    else:
        res="注册失败，手机号已注册"
    return json.dumps(res)


# 函数userlogin
# 作用：微信小程序用户登录路由，获取用户登录信息，判断是否存在，返回登录结果
# 作者：王明
# 完成时间：2019/08/28
@app.route('/userlogin',methods=['GET','POST'])
def userlogin():
    db = MhDatabases()
    # 获取微信小程序端传来的id和password
    id = str(json.loads(request.values.get("id")))
    password=str(json.loads(request.values.get("password")))
    print("id",id)
    print("password",password)

    # 根据ID在数据库中查询用户数据
    result=db.executeQuery("select * from user where phone=%s",[id])
    print(result)

    if len(result)!=0:
        if result[0][1]==password:
        # 如果匹配返回登录成功
            res='登录成功'
            return json.dumps(res)
    else:
        # 如果不匹配返回账号或密码错误
        res='账号或密码错误'
        return json.dumps(res)


# 函数allorders
# 作用：微信小程序用户全部订单路由，获取用户id，返回按时间整合的用户所有订单
# 作者：王明
# 完成时间：2019/08/28
@app.route('/allorders',methods=['GET','POST'])
def allorders():
    db = MhDatabases()
    # 获取微信小程序端传来的ID
    id = str(json.loads(request.values.get("id")))
    print("id",id)

    # 根据ID在数据库中查询用户订单数据
    result = db.executeQuery("select gid,name,sum(number),uprice,image,time from pcr where optype=10 and isdelete=0 and buyerid=%s group by name,time",[id])
    timeresult = db.executeQuery("select time from pcr where optype=10 and isdelete=0 and buyerid=%s group by time", [id])
    column=['gid','name','number','uprice','image']
    print(result)
    timess=[]
    for i in timeresult:
        timess.append(i[0])
    # 返回查询到的结果:
    # 如果有订单，按时间整合订单信息，转为json格式发送给微信小程序端订单的详细信息
    if len(result)!=0 :
        total=[]
        total2=[]
        totalprice=[]
        for i in range(0,len(timeresult)):
            totalprice.append(0)
        for t in range(0,len(timess)):
            for i in range(0,len(result)):
                    if result[i][5]==timess[t] :
                        a={}
                        a[column[0]]=result[i][0]
                        a[column[1]] = result[i][1]
                        a[column[2]] = int(result[i][2])
                        a[column[1]] = result[i][3]
                        a[column[4]] = "http://139.217.130.233/"+result[i][4]
                        totalprice[t]+=float(result[i][2])*result[i][3]
                        total.append(a)
            total2.append(total)
            total=[]
            totalprice[t]=round(totalprice[t],2)
        res=[]

        for i in range(0,len(total2)):
            order={"orders":total2[i],"time":timess[i],"totalprice":totalprice[i]}
            res.append(order)
        print(res)
        return json.dumps(res)

    # 如果没有订单，返回暂无订单
    else:
        res="暂无订单"
        return json.dumps(res)


# 函数deleteorders
# 作用：微信小程序用户删除订单路由，获取用户id和想要删除的订单时间，修改该订单在数据库中的isdelete项
# 作者：王明
# 完成时间：2019/08/28
@app.route('/deleteorders',methods=['GET','POST'])
def deleteorders():
    db = MhDatabases()
    # 获取微信小程序端传来的ID和订单完成时间
    id = str(json.loads(request.values.get("id")))
    time = str(json.loads(request.values.get("times")))
    print("id",id," time",time)

    # 根据ID和订单完成时间修改该订单在数据库中的isdelete项
    result=db.executeUpdate("update pcr set isdelete=true where buyerid=%s and time=%s and optype=10 ",[id,time])

    # 返回删除的结果:
    if result==0:
        res="删除失败"
    else:
        res="删除成功"
    return json.dumps(res)



# 函数orderdetail
# 作用：微信小程序用户订单详情路由，获取用户id和订单时间，返回数据库中订单的详细信息
# 作者：王明
# 完成时间：2019/08/28
@app.route('/orderdetail',methods=['GET','POST'])
def ordersdetail():
    db = MhDatabases()
    # 获取微信小程序端传来的ID和订单完成时间
    id = str(json.loads(request.values.get("id")))
    time = str(json.loads(request.values.get("time")))
    print("id",id," time",time)

    # 根据ID和订单完成时间查询在数据库中的数据
    result = db.executeQuery("select gid,name,sum(number),uprice,image from pcr where buyerid=%s and time=%s and isdelete=0 and optype=10 group by name",[id,time])

    # 返回查询的结果:
    if len(result)!=0:
        list=[]
        totalprice=0
        for i in result:
            dict={}
            dict['gid']=i[0]
            dict['name']=i[1]
            dict['number']=int(i[2])
            dict['uprice']=i[3]
            dict['total']=float(i[2])*i[3]
            dict['image'] =  "http://139.217.130.233/"+i[4]
            list.append(dict)
        res={"orders":list}
    else:
        res="无订单"
    return json.dumps(res)


# 函数shoppingcart
# 作用：微信小程序用户购物车路由，获取用户id，从数据库查询用户加入购物车的商品信息，发送给微信小程序端
# 作者：王明
# 完成时间：2019/08/29
@app.route('/shoppingcart',methods=['GET','POST'])
def shoppingcart():
    db = MhDatabases()
    # 获取微信小程序端传来的用户id
    id = str(json.loads(request.values.get("id")))
    print(id)

    result=db.executeQuery("select image,gid,name,sum(number),uprice  from pcr where buyerid=%s and isdelete=0 and optype=5 group by name",[id])
    # 返回查询的结果:
    if len(result) != 0:
        res = []

        for i in result:
            dict = {}
            result1=db.executeQuery("select number from goods where gid=%s ",[i[1]])
            dict['imgSrc'] = "http://139.217.130.233/"+i[0]
            dict['title'] = i[2]
            dict['gid'] = i[1]
            dict['price'] = i[4]
            dict['quantity'] = int(i[3])
            dict['max']=result1[0][0]
            res.append(dict)
    else:
        res = "空"
    return json.dumps(res)




# 函数cartsettle
# 作用：微信小程序用户购物车结算路由，获取用户发送的id，订单时间，结算商品数组，修改数据库相关信息
# 作者：王明
# 完成时间：2019/08/29
@app.route('/cartsettle',methods=['GET','POST'])
def cartsettle():
    db = MhDatabases()
    # 获取微信小程序端传来的商品id，订单时间，结算商品数组
    id = str(json.loads(request.values.get("id")))
    time = str(json.loads(request.values.get("time")))
    scart=json.loads(request.values.get("scart"))
    print(id,time,scart)
    for i in scart:
        order=[]
        result = db.executeQuery("select name,image,sort,number from goods where gid=%s",[i['gid']]) # 获取商品信息
        print(result)
        if len(result)!=0:
            order.append(result[0][1])  # image
            order.append( i['gid']) # gid
            order.append(result[0][0]) # name
            order.append(result[0][2]) # sort
            gnumber=result[0][3]-int(i['quantity']) # gnumber
            order.append( int(i['quantity'])) # number
            order.append(float(i['price'])) # uprice
            order.append(int(i['quantity'])*float(i['price'])) # total
            order.append(time) # time
            order.append(id) # buyerid
            order.append(10) # optype
            order.append(0) # isdelete
            if gnumber<0:
                res="库存不足"
            else:
                db.executeUpdate("update goods set number=%s where gid=%s",[gnumber,order[1]]) # 修改商品库存
                db.executeUpdate("update pcr set isdelete=1 where gid=%s and buyerid=%s and optype=5", [order[1],order[8]]) # 修改加入购物车订单isdelete项
                db.executeUpdate("insert into pcr values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", order) # 添加购买记录
                res="结算成功"
        else:
            res="结算失败"

    return json.dumps(res)


# 函数cartdelete
# 作用：微信小程序用户购物车删除路由，获取用户发送的id，删除商品数组，修改数据库相关信息
# 作者：王明
# 完成时间：2019/08/29
@app.route('/cartdelete',methods=['GET','POST'])
def cartdelete():
    db = MhDatabases()
    # 获取微信小程序端传来的商品id，删除商品数组
    id = str(json.loads(request.values.get("id")))
    scart=json.loads(request.values.get("scart"))
    for i in scart:
        db.executeUpdate("update pcr set isdelete=1 where gid=%s and buyerid=%s and optype=5",[i['gid'],id]) # 修改订单isdelete项
    res="删除成功"
    return json.dumps(res)

# 函数cartadd
# 作用：微信小程序用户购物车添加路由，获取用户发送的信息，修改数据库相关信息
# 作者：王明
# 完成时间：2019/08/29
@app.route('/cartadd',methods=['GET','POST'])
def cartadd():
    db = MhDatabases()
    # 获取微信小程序端传来的用户id，商品信息
    id = str(json.loads(request.values.get("id")))
    gid = str(json.loads(request.values.get("gid")))
    quantity = int(json.loads(request.values.get("quantity")))
    time = str(json.loads(request.values.get("time")))
    result=db.executeQuery("select image,name,sort,uprice,number from goods where gid=%s",[gid]) # 获取商品在数据库中的详细信息
    print(result)

    if result[0][4]-quantity<0:
        res="库存不足"
    else:
        order=[]
        price=result[0][3]
        order.append(result[0][0])
        order.append(gid)
        order.append(result[0][1])
        order.append(result[0][2])
        order.append(quantity)
        order.append(price)
        order.append(quantity*price)
        order.append(time)
        order.append(id)
        order.append(5)
        order.append(0)
        r=db.executeUpdate("insert into pcr values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", order) # 添加加入购物车记录
        if r==1:
            res="添加成功"
        else:
            res="添加失败"
    return json.dumps(res)

#函数cartchange
#作用：微信小程序用户增减购物车商品数量路由，获取用户id,商品id,此商品购物车中数量id,返回是否数据库修改成功
#作者：陶一丁
#完成时间：2019/9/9
@app.route('/cartchange',methods=['GET','POST'])
def cartchange():
    db = MhDatabases()

    id = str(json.loads(request.values.get("id")))
    gid = str(json.loads(request.values.get("gid")))
    quantity = int(json.loads(request.values.get("quantity")))

    r = db.executeUpdate("update pcr set number=%s where gid=%s and buyerid=%s and optype=5",[quantity,gid,id])

    if r == 1:
        res ="修改失敗"
    else:
        res = "修改成功"

    return json.dumps(res)

# 函数goodsdetail
# 作用：微信小程序用户商品详情路由，获取用户发送的商品id，返回数据库中的商品详细信息
# 作者：王明
# 完成时间：2019/09/2
@app.route('/goodsdetail',methods=['GET','POST'])
def goodsdetail():
    db = MhDatabases()
    # 获取微信小程序端传来的商品id
    gid = str(json.loads(request.values.get("gid")))
    print(gid)
    result = db.executeQuery("select image,name,number,uprice,location from goods where gid=%s", [gid]) # 从数据库中查询商品详细信息
    res=[]
    if len(result) != 0:

        for i in result:
            dict = {}
            dict['imgSrc'] = "http://139.217.130.233/" + i[0]
            dict['name'] = i[1]
            dict['price'] = i[3]
            dict['storage'] = i[2]
            dict['location'] = i[4]
            res.append(dict)
    else:
        res = "空"
    return json.dumps(res)



# 函数hotmain
# 作用：微信小程序用户主界面热销商品路由，获取用户发送的id，根据商品销量返回当月热销商品
# 作者：王明
# 完成时间：2019/09/2
@app.route('/hotmain',methods=['GET','POST'])
def hotmain():
    db = MhDatabases()
    # 获取微信小程序端传来的用户id
    id = str(json.loads(request.values.get("id")))
    print(id)

    res = []
    h = mhHot()
    hot = h.hot(h.getPcr(), 10) # 获取当月热销前三的商品名称和销量
    if len(hot)==0:
        res="暂无商品"
    else:
        for i in hot:
            result = db.executeQuery("select gid,name,image,uprice from goods where name=%s", [i[0]]) # 获取热销商品详细信息
            dict = {}
            dict['gid'] = result[0][0]
            dict['name'] = result[0][1]
            dict['image'] = "http://139.217.130.233/" + result[0][2]
            dict['uprice'] = result[0][3]
            dict['sales'] = i[1]
            res.append(dict)
    return json.dumps(res)

# 函数recommendmain
# 作用：微信小程序用户主界面热销商品路由，获取用户发送的id，根据商品销量返回当月热销商品
# 作者：王明
# 完成时间：2019/09/2
@app.route('/recommendmain',methods=['GET','POST'])
def recommendmain():
    db = MhDatabases()
    # 获取微信小程序端传来的用户id
    id = str(json.loads(request.values.get("id")))
    print(id)

    res=[]
    mh = mhitemCF()
    data = mh.getUidScoreBid()  # 获得数据
    W = mh.similarity(data);  # 算物品相似矩阵
    relist=mh.recommandList(data, W, id, 10, 10);  # 推荐
    if len(relist)==0:
        res="暂无推荐"
    else:
        for i in relist:
            result = db.executeQuery("select gid,name,image,uprice from goods where name=%s", [i[0]])  # 获取推荐商品详细信息
            dict = {}
            dict['gid'] = result[0][0]
            dict['name'] = result[0][1]
            dict['image'] = "http://139.217.130.233/" + result[0][2]
            dict['uprice'] = result[0][3]
            res.append(dict)
    return json.dumps(res)

# 函数idcodelogin
# 作用：微信小程序用户验证码登录路由，获取用户发送的id，查询是否存在，如果不存在添加记录
# 作者：王明
# 完成时间：2019/09/2
@app.route('/idcodelogin',methods=['GET','POST'])
def idcodelogin():
    db = MhDatabases()
    # 获取微信小程序端传来的用户id
    id = str(json.loads(request.values.get("id")))
    print(id)
    result=db.executeQuery("select * from user where phone=%s",[id]) # 查询id在数据库是否已存在
    if len(result)==0:
        db.executeUpdate("insert into user values(%s,null,null,null) ",[id])
    res="成功"
    return json.dumps(res)

# 函数mine
# 作用：微信小程序用户mine界面渲染路由，获取用户发送的id，返回用户个人详细信息
# 作者：王明
# 完成时间：2019/09/2
@app.route('/mine',methods=['GET','POST'])
def mine():
    db = MhDatabases()
    # 获取微信小程序端传来的用户id
    id = str(json.loads(request.values.get("id")))
    print(id)
    result = db.executeQuery("select name from user where phone=%s",[id])  # 查询id在数据库中的name
    if len(result)!=0:
        if result[0][0]==None:
            res="用户昵称为空"
        else:
            res=result[0][0]
    else:
        res = "用户昵称为空"
    return json.dumps(res)

# 函数updatemine
# 作用：微信小程序完善用户个人信息路由，获取用户发送的个人信息，修改数据库相关数据
# 作者：王明
# 完成时间：2019/09/2
@app.route('/updatemine',methods=['GET','POST'])
def updatemine():
    db = MhDatabases()
    # 获取微信小程序端传来的用户修改信息
    name = str(json.loads(request.values.get("name")))
    sex = str(json.loads(request.values.get("sex")))
    id = str(json.loads(request.values.get("id")))
    password = str(json.loads(request.values.get("password")))
    result=db.executeUpdate("update user set pwd=%s,gender=%s,name=%s where phone=%s",[password,sex,name,id]) # 修改用户在数据库中的个人信息记录
    if result==0:
        res="修改失败"
    else:
        res="修改成功"
    return json.dumps(res)

# 函数sortchart
# 作用：微信小程序图表路由，获取用户发送的id，按种类发送总金额数据给小程序
# 作者：王明
# 完成时间：2019/09/4
@app.route('/sortchart',methods=['GET','POST'])
def sortchart():
    db = MhDatabases()
    # 获取微信小程序端传来的id
    id = str(json.loads(request.values.get("id")))
    #从数据库中查询数据---生成Json格式
    result = db.executeQuery(
        "select sort,sum(cast(total as decimal(18,1))) from pcr where optype=10 and buyerid=%s and str_to_date(time,'%%Y/%%m/%%d %%H:%%i:%%s')>date_format(curdate(),'%%Y/%%m/01 00:00:00') group by sort",[id])

    result2=db.executeQuery("select sort from goods group by sort")
    r=[]
    for i in result:
        r.append(i[0])
    ress =[]
    totalprice=0;
    for i in result:
        dict = {}
        dict["sort"] = i[0]
        dict["total"] = float(i[1])
        totalprice += float(i[1])
        ress.append(dict)
    for i in range(0, len(result2)):
        if result2[i][0] not in r:
            dict = {}
            dict["sort"] = result2[i][0]
            dict["total"] = 0
            ress.append(dict)
    t=round(totalprice,2)
    res={"result":ress,"totalprice":t}
    content = json.dumps(res)
    return content

# 函数searchgoods
# 作用：微信小程序查询商品路由，支持模糊搜索
# 作者：王明
# 完成时间：2019/09/4
@app.route('/searchgoods',methods=['GET','POST'])
def searchgoods():
    db = MhDatabases()
    search= str(json.loads(request.values.get("search")))
    result=db.executeQuery("select * from goods where name like '%%%%%s%%%%'"%(search))
    res=[]
    if len(result)!=0:
        for i in result:
            dict = {}
            dict['gid'] = i[0]
            dict['name'] = i[1]
            dict['image'] = "http://139.217.130.233/" + i[2]
            dict['uprice'] = i[5]
            res.append(dict)
        return json.dumps(res)
    else:
        res="空"
        return json.dumps(res)



if __name__ == '__main__':
    app.run(ssl_context='adhoc')