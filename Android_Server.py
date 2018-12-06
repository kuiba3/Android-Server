from socketserver import (TCPServer as TCP,StreamRequestHandler as SRH)
from time import ctime
import pymysql
import datetime

HOST = ''
PORT = 6543

ADDR = (HOST, PORT)

def database():
    db = pymysql.connect('localhost','root','12345','server')
    return db

class MyRequestHandler(SRH):
    def handle(self):
        ## 获取数据的种类
        data_type = self.request.recv(1024).strip().decode()

        print('...connected from:', self.client_address, ctime())
        print('type is',data_type)

        if data_type != "keyword_message" and data_type != "QW":
            data = self.request.recv(1024).strip().decode()
            datadict = eval(data)
            print(data)
            print(datadict)

        else:
            lengthstr = self.request.recv(1024).strip().decode()
            print(lengthstr)
            lengthdict = eval(lengthstr)
            length = lengthdict["length"]
            IMEI = ''

            for i in range(0,length):
                data = self.request.recv(4 * 1024).strip().decode()
                datadict = eval(data)
                #print(data)
                print(datadict)

                ## 处理获得的短信信息
                if data_type == "keyword_message":
                    if i == 0:
                        IMEI = datadict['IMEI']
                    else:
                        print(IMEI)
                        Message(datadict,IMEI)
                elif data_type == "QW":
                    print("处理QW信息")
                    QW(datadict)

        if data_type == "keyword_contact":
            Contact(datadict)
        elif data_type == "permission":
            Permission(datadict)

        elif data_type == "appName":
            App(datadict)

        send_data = (data_type + str(" ok")).encode('utf-8')
        self.request.send(send_data)
        print("send OK :", send_data)

def Contact(data):
    ## 获取IMEI的值
    IMEI = data['IMEI']

    ## 连接数据库并获取连接对象
    db = database()
    cur = db.cursor()

    ## 获取联系人的信息，并查询电话号码在数据库中是否存在
    ## 如果不存在，添加到数据库
    ## 如果存在，更新数据库中的联系人信息
    number = ''
    for d in data:
        if d != 'IMEI':
            name = list(data[d])[0]
            number = data[d][name]

            selectsql = "select * from contact where IMEI = '{}' and number = '{}' ".format(IMEI,number)
            cur.execute(selectsql)
            print("rowcount is ",cur.rowcount)
            if cur.rowcount > 0:
                updatesql = "update contact set contact_name = '{}' where IMEI = '{}' and number = '{}' " \
                            .format(name,IMEI,number)
                try:
                    cur.execute(updatesql)
                    db.commit()
                except:
                    db.rollback()
            else:
                insertsql = "insert into contact(IMEI,contact_name,number) values" \
                            "('{}','{}','{}')".format(IMEI,name,number)
                try:
                    cur.execute(insertsql)
                    db.commit()
                except:
                    db.rollback()

    db.close()

def Message(data,IMEI):

    ## 连接数据库并获取连接对象
    db = database()
    cur = db.cursor()

    number = data['number']
    message_type = data['type']
    date = data['date']
    person = data['person']
    body = data['body']


    ## 使用条件 IMEI,number,type,date 在数据库中查询，如果存在，则不用操作
    ## 否则，添加短信到数据库中
    selectsql = "select * from message where IMEI = '{}' and contact_number = '{}' " \
                "and type = '{}' and date = '{}'".format(IMEI,number,message_type,date)
    cur.execute(selectsql)

    if cur.rowcount == 0:
        insertsql = "insert into message(IMEI,contact_name,contact_number,type,date,body) values" \
                    "('{}','{}','{}','{}','{}','{}')".format(IMEI, person, number,message_type,date,body)

        try:
            cur.execute(insertsql)
            db.commit()
        except:
            db.rollback()

    db.close()

def Permission(data):
    ## 获取IMEI的值
    IMEI = data['IMEI']

    ## 连接数据库并获取连接对象
    db = database()
    cur = db.cursor(cursor=pymysql.cursors.DictCursor)

    ## -----更新数据库中的App权限-----
    ## 查询数据库中此IMEI号的所有权限信息，存储在列表perlist中
    ## 判断权限是否在列表perlist中，如果不在，在数据库中插入一条权限
    ## 如果在，删除列表perlist中的此权限
    ## 最后，把剩下在列表perlist中的权限，从数据库中删除
    perlist = []
    selectsql = "select * from permission where IMEI = '{}'".format(IMEI)
    try:
        cur.execute(selectsql)
        num = cur.rowcount
        for i in range(num):
            a = cur.fetchone()
            perlist.append(a['permission'])
    except Exception as e:
        print(e)

    for d in data:
        if d != "IMEI":
            permission = data[d]
            if permission in perlist:
                perlist.remove(permission)
            else:
                insertsql = "insert into permission(IMEI,permission) values('{}','{}')".format(IMEI,permission)
                try:
                    cur.execute(insertsql)
                    db.commit()
                except Exception as e:
                    print(e)
                    db.rollback()

    for per in perlist:
        deletesql = "delete from permission where IMEI = '{}' and permission = '{}'".format(IMEI,per)
        print("oooooooooooooo")
        print(deletesql)
        try:
            cur.execute(deletesql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()

    db.close()

def App(data):
    ## 获取IMEI的值
    IMEI = data['IMEI']

    ## 连接数据库并获取连接对象
    db = database()
    cur = db.cursor(cursor=pymysql.cursors.DictCursor)

    ## -----更新数据库中手机违规软件-----
    ## 查询数据库中此IMEI号的所有违规软件信息，存储在列表applist中
    ## 判断软件是否在列表applist中，如果不在，在数据库中插入一条权限
    ## 如果在，删除列表applist中的此权限
    ## 最后，把剩下在列表applist中的软件信息，从数据库中删除
    applist = []
    selectsql = "select * from app where IMEI = '{}'".format(IMEI)
    try:
        cur.execute(selectsql)
        num = cur.rowcount
        for i in range(num):
            a = cur.fetchone()
            applist.append(a['permission'])
    except Exception as e:
        print(e)

    for d in data:
        if d != "IMEI":
            app = data[d]
            if app in applist:
                applist.remove(app)
            else:
                insertsql = "insert into app(IMEI,app) values('{}','{}')".format(IMEI,app)
                try:
                    cur.execute(insertsql)
                    db.commit()
                except Exception as e:
                    print(e)
                    db.rollback()

    for app in applist:
        deletesql = "delete from app where IMEI = '{}' and app = '{}'".format(IMEI,app)
        try:
            cur.execute(deletesql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()

    db.close()

def QW(data):
    # 连接数据库并获取连接对象
    db = database()
    cur = db.cursor()
    print(data)

    IMEI = data['IMEI']
    jilustr = data['记录']
    jilu = eval(jilustr)
    print(jilu,type(jilu))
    app  = jilu['软件']
    body = jilu['内容']


    nowtime = datetime.datetime.now()
    time = datetime.datetime.strftime(nowtime, '%Y-%m-%d %H:%M')




    insertsql = "insert into qw(IMEI,App,Body,Time) values" \
                "('{}','{}','{}','{}')".format(IMEI, app, body, time)

    try:
        cur.execute(insertsql)
        db.commit()
    except:
        db.rollback()

    db.close()




if __name__ == '__main__':
    tcpServ = TCP(ADDR, MyRequestHandler)

    print('waiting for connection...')
    tcpServ.serve_forever()
