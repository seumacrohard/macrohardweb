from functools import wraps
import os
from flask import Flask, render_template, request, session, redirect, url_for, json
from MhDatabses import MhDatabases
from mhHot import mhHot

app = Flask(__name__)

app.secret_key = 'test' # 设置secret_key

#管理员登录验证
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


#管理员登录界面
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


# 管理员界面账单管理
@app.route('/billList', methods=['GET', 'POST'])
@login_required
def billList():
    # 连接数据库
    db=MhDatabases()
    if request.method == 'GET':
        # 从数据库中返回最近五条交易记录并返回
        result = db.executeQuery("select image,gid,name ,sort,uprice,sum(number),sum(total) from pcr group by name")
        return render_template("billList.html",result=result)
    else:
        # 获取商品ID或者名称
        product = request.form.get("product")
        print(product)
        result1 = db.executeQuery("select image,gid,name ,sort,uprice,sum(number),sum(total) from pcr where gid=%s group by name", [product])
        result2 = db.executeQuery("select image,gid,name ,sort,uprice,sum(number),sum(total) from pcr where name=%s group by name", [product])
        if len(result1)!=0 :
            # 根据商品ID从数据库获取交易信息，如果不存在返回“无此交易记录”
            result=result1
        elif len(result2)!=0 :
            # 根据商品名称从数据库获取交易信息，如果不存在返回“无此交易记录”
            result=result2
        else:
            result="暂无记录"
        return render_template("billList.html",result=result)


#管理员商品管理界面
@app.route('/product', methods=['GET', 'POST'])
@login_required
def product():
    # 连接数据库
    db = MhDatabases()
    if request.method == 'GET':
        # 从数据库中查找商品信息并返回
        result = db.executeQuery("select * from goods")
        return render_template("product.html",result=result)
    else:
        # 获取商品ID
        proID=request.form.get("proid")
        print("proID",proID)
        pid=request.form.get("pid")
        print("pid",pid)
        if proID:
            # 从数据库获取商品信息并返回
            result = db.executeQuery("select * from goods where gid=%s",[proID])
            return render_template("product.html",result=result)
        if pid :
            # 返回商品修改界面
            return redirect(url_for('update',pid=pid))

# 管理员界面商品添加
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # 连接数据库
    db = MhDatabases()
    if request.method == 'GET':
        return render_template("add.html")
    else:
        # 获取要添加的商品信息
        img=request.files.get("myFile")
        fname=img.filename
        filepath="./static/img/"+fname
        img.save(os.path.join("./static/img/",fname))
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
        # img.save(filepath)
        # 查询数据库中是否已存在该商品，如果不存在则向数据库添加商品信息
        result1 = db.executeQuery("select * from goods where gid=%s", [product[0]])
        result2 = db.executeQuery("select * from goods where name=%s",[product[1]])
        if len(result1) == 0 and len(result2) == 0:
            result = db.executeUpdate("insert into goods values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",product)
        else:
            result = 0
        return render_template("add.html",data=result)

# 管理员界面商品修改查看
@app.route('/update?<string:pid>', methods=['GET', 'POST'])
@login_required
def update(pid):
    # 连接数据库
    db = MhDatabases()
    if request.method == 'GET':
        # 从数据库获取商品信息并返回
        result = db.executeQuery("select * from goods where gid=%s",[pid])
        # print(result)
        return render_template("update.html",result=result)
    else:

        gid=request.form.get("productId")
        print(gid)
        if gid:
            # 在数据库中删除商品信息
            db.executeUpdate("delete from goods where gid=%s",[gid])
            return redirect(url_for('product'))
        else:
            # 获取商品可修改的信息
            product = []
            product.append(request.form.get("type"))
            product.append(int(request.form.get("number")))
            product.append(float(request.form.get("price")))
            print(product)

            # 在数据库中修改商品信息
            db.executeUpdate("update goods set sort=%s,number=%s,uprice=%s where gid=%s",[product[0],product[1],product[2],pid])
            return redirect(url_for('product'))

# 管理员界面生成图表
@app.route("/showEcharts",methods=["GET","POST"])
@login_required
def showEcharts():
    #从数据库中查询数据---生成Json格式
    helper = MhDatabases()
    result=helper.executeQuery("select name,sum(total) from pcr group by name ")
    print(result)
    list =[]
    for i in result:
        dict ={}
        dict["name"]=i[0]   #上衣
        dict["total"]=i[1]  #966
        list.append(dict)
    res = {"result":list}
    content = json.dumps(res)
    return content
# 管理员界面生成图表
@app.route("/showEchart")
@login_required
def showEchart():
    return  render_template("echarts.html")


#微信小程序用户注册
@app.route('/userregister',methods=['GET','POST'])
def userregister():
    # 连接数据库
    db=MhDatabases()
    # 获取微信小程序端传来的ID和password
    id = str(json.loads(request.values.get("id")))
    password=str(json.loads(request.values.get("password")))
    name = str(json.loads(request.values.get("name")))
    sex = str(json.loads(request.values.get("sex")))
    print("name",name," sex",sex," id",id," password",password)

    # 根据ID在数据库中查询用户数据
    result1=db.executeQuery("select * from user where phone=%s",[id])
    if len(result1) == 0:
        result = db.executeUpdate("insert into user values(%s,%s,%s,%s)", [id,password,sex,name])
        res = "注册成功"
    else:
        res="注册失败，手机号已注册"
    return json.dumps(res)


#微信小程序用户登录
@app.route('/userlogin',methods=['GET','POST'])
def userlogin():
    # 连接数据库
    db=MhDatabases()

    # 获取微信小程序端传来的ID和password
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


# 微信小程序全部订单
@app.route('/allorders',methods=['GET','POST'])
def allorders():
    # 连接数据库
    db=MhDatabases()

    # 获取微信小程序端传来的ID
    id = str(json.loads(request.values.get("id")))
    print("id",id)

    # 根据ID在数据库中查询用户订单数据
    result=db.executeQuery("select gid,name,number,uprice,total,image,time from pcr where optype=10 and isdelete=0 and buyerid=%s",[id])
    column=['gid','name','number','uprice','total','image','time']
    print(result)
    # print (column)

    # 返回查询到的结果:
    # 如果有订单，按时间整合发送给微信小程序端
    if len(result)!=0:
        time=result[0][6]
        total=[]
        total2=[]
        totalprice=[]
        for i in range(0,len(result)):
            totalprice.append(0)
        timess=[]
        timess.append(time)
        k=0
        for i in range(0,len(result)):
            n=i+1

            if n<len(result):
                if result[i][6]==time and result[n][6]==time:
                    a={}
                    for j in range(0,4):
                        a[column[j]]=result[i][j]
                    a[column[5]] = "http://10.203.209.181:5000/"+result[i][5]
                    totalprice[k]+=result[i][4]
                    total.append(a)
                if result[i][6]==time and result[n][6]!=time:
                    time=result[n][6]
                    timess.append(time)
                    totalprice[k]+=result[i][4]
                    a = {}
                    for j in range(0,4):
                        a[column[j]] = result[i][j]
                    a[column[5]] = "http://10.203.209.181:5000/" + result[i][5]
                    total.append(a)
                    total2.append(total)
                    total=[]
                    k=k+1
            else:
                totalprice[k] += result[i][4]
                a = {}
                for j in range(0,4):
                    a[column[j]] = result[i][j]
                a[column[5]] = "http://10.203.209.181:5000/" + result[i][5]
                total.append(a)
                total2.append(total)
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



#微信小程序删除订单
@app.route('/deleteorders',methods=['GET','POST'])
def deleteorders():
    # 连接数据库
    db=MhDatabases()

    # 获取微信小程序端传来的ID和订单完成时间
    id = str(json.loads(request.values.get("id")))
    time = str(json.loads(request.values.get("times")))
    print("id",id," time",time)

    # 根据ID和订单完成时间删除在数据库中的数据
    result=db.executeUpdate("update pcr set isdelete=true where buyerid=%s and time=%s and optype=10",[id,time])

    # 返回删除的结果:
    if result==1:
        res="删除成功"
    else:
        res="删除失败"
    return json.dumps(res)



#微信小程序订单详情
@app.route('/orderdetail',methods=['GET','POST'])
def ordersdetail():
    # 连接数据库
    db=MhDatabases()

    # 获取微信小程序端传来的ID和订单完成时间
    id = str(json.loads(request.values.get("id")))
    time = str(json.loads(request.values.get("time")))
    print("id",id," time",time)

    # 根据ID和订单完成时间查看在数据库中的数据
    result = db.executeQuery("select gid,name,number,uprice,total,image from pcr where buyerid=%s and time=%s and isdelete=0 and optype=10",[id,time])

    # 返回查询的结果:
    if len(result)!=0:
        list=[]
        totalprice=0
        for i in result:
            dict={}
            dict['gid']=i[0]
            dict['name']=i[1]
            dict['number']=i[2]
            dict['uprice']=i[3]
            dict['total']=i[4]
            dict['image'] =  "http://10.203.209.181:5000/"+i[5]
            list.append(dict)
        res={"orders":list}
    else:
        res="无订单"
    return json.dumps(res)


#微信小程序购物车
@app.route('/shoppingcart',methods=['GET','POST'])
def shoppingcart():
    # 连接数据库
    db=MhDatabases()
    # 获取微信小程序端传来的商品id
    id = str(json.loads(request.values.get("id")))
    print(id)

    result=db.executeQuery("select image,gid,name,gnumber,number,uprice ,time from pcr where buyerid=%s and isdelete=0 and optype=5",[id])
    # 返回查询的结果:
    if len(result) != 0:
        res = []

        for i in result:
            dict = {}
            dict['imgSrc'] = "http://10.203.209.181:5000/"+i[0]
            dict['title'] = i[2]
            dict['gid'] = i[1]
            dict['price'] = i[5]
            dict['quantity'] = i[4]
            dict['max']=i[3]
            dict['time']=i[6]
            res.append(dict)
    else:
        res = "空"
    return json.dumps(res)



#微信小程序购物车结算
@app.route('/cartsettle',methods=['GET','POST'])
def cartsettle():
    # 连接数据库
    db = MhDatabases()
    # 获取微信小程序端传来的商品id
    id = str(json.loads(request.values.get("id")))
    time = str(json.loads(request.values.get("time")))
    scart=json.loads(request.values.get("scart"))
    print(type(scart))
    print(scart)
    for i in scart:
        order=[]
        result = db.executeQuery("select name,image,sort,number from goods where gid=%s",[i['gid']])
        print(result)
        if len(result)!=0:
            order.append(result[0][1])  #image
            order.append( i['gid'])#gid
            order.append(result[0][0])# name
            order.append(result[0][2])# sort
            order.append(result[0][3]-int(i['quantity']))# gnumber
            order.append( int(i['quantity']))# number
            order.append(float(i['price'])) # uprice
            order.append(int(i['quantity'])*float(i['price']))# total
            order.append(time)# time
            order.append(id) # buyerid
            order.append(10) # optype
            order.append(0) # isdelete
            db.executeUpdate("update goods set number=%s where gid=%s",[order[4],order[1]])
            db.executeUpdate("update pcr set isdelete=1 where gid=%s and buyerid=%s and optype=5", [order[1],order[9]])
            db.executeUpdate("insert into pcr values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", order)
        else:
            res="结算"
    res="结算成功"
    return json.dumps(res)

#微信小程序删除购物车
@app.route('/cartdelete',methods=['GET','POST'])
def cartdelete():
    # 连接数据库
    db = MhDatabases()
    # 获取微信小程序端传来的商品id
    id = str(json.loads(request.values.get("id")))
    scart=json.loads(request.values.get("scart"))
    for i in scart:
        db.executeUpdate("update pcr set isdelete=1 where gid=%s and buyerid=%s and optype=5",[i['gid'],id])
    res="删除成功"
    return json.dumps(res)

# 微信小程序添加购物车
@app.route('/cartadd',methods=['GET','POST'])
def cartadd():
    # 连接数据库
    db = MhDatabases()
    # 获取微信小程序端传来的商品id
    id = str(json.loads(request.values.get("id")))
    gid = str(json.loads(request.values.get("gid")))
    quantity = int(json.loads(request.values.get("quantity")))
    time = str(json.loads(request.values.get("time")))
    result=db.executeQuery("select image,name,sort,number,uprice from goods where gid=%s",[gid])
    print(result)
    order=[]
    price=result[0][4]
    order.append(result[0][0])
    order.append(gid)
    order.append(result[0][1])
    order.append(result[0][2])
    order.append(result[0][3])
    order.append(quantity)
    order.append(price)
    order.append(quantity*price)
    order.append(time)
    order.append(id)
    order.append(5)
    order.append(0)
    r=db.executeUpdate("insert into pcr values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", order)
    if r==1:
        res="添加成功"
    else:
        res="添加失败"
    return json.dumps(res)


#微信小程序商品详情
@app.route('/goodsdetail',methods=['GET','POST'])
def goodsdetail():
    # 连接数据库
    db=MhDatabases()

    # 获取微信小程序端传来的商品id
    gid = str(json.loads(request.values.get("gid")))
    print(gid)
    result = db.executeQuery("select image,name,number,uprice,location from goods where gid=%s", [gid])
    res=[]
    if len(result) != 0:

        for i in result:
            dict = {}
            dict['imgSrc'] = "http://10.203.209.181:5000/" + i[0]
            dict['name'] = i[1]
            dict['price'] = i[3]
            dict['storage'] = i[2]
            dict['location'] = i[4]
            res.append(dict)
    else:
        res = "空"
    return json.dumps(res)



#微信小程序用户主界面
@app.route('/hotmain',methods=['GET','POST'])
def hotmain():
    # 连接数据库
    db = MhDatabases()

    # 获取微信小程序端传来的商品id
    id = str(json.loads(request.values.get("id")))
    print(id)

    res = []
    h = mhHot()
    hot = h.hot(h.getPcr(), 3)
    if len(hot)==0:
        res="暂无商品"
    else:
        for i in hot:
            result = db.executeQuery("select gid,name,image,uprice from goods where name=%s", [i[0]])
            dict = {}
            dict['gid'] = result[0][0]
            dict['name'] = result[0][1]
            dict['image'] = "http://10.203.209.181:5000/" + result[0][2]
            dict['uprice'] = result[0][3]
            dict['sales'] = i[1]
            res.append(dict)
    '''if len(result) != 0:

        for i in result:
            dict = {}
            dict['gid']=i[0]
            dict['name'] = i[1]
            dict['image'] = "http://10.203.209.181:5000/" + i[2]
            dict['sort'] = i[3]
            dict['number'] = i[4]
            dict['uprice'] = i[5]
            dict['location'] = i[6]
            res.append(dict)
    else:
        res = "空"    '''
    return json.dumps(res)






if __name__ == '__main__':
    # CORS(app,supports_credentials=True)
    app.run(ssl_context='adhoc')
