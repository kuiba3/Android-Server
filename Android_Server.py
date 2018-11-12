from socketserver import (TCPServer as TCP,StreamRequestHandler as SRH)
from time import ctime
import pymysql

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

        if data_type != "keyword_message":
            data = self.request.recv(1024).strip().decode()
            datadict = eval(data)
            #print(data)
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
                if i == 0:
                    IMEI = datadict['IMEI']
                else:
                    print(IMEI)
                    Message(datadict,IMEI)

        if data_type == "keyword_contact":
            Contact(datadict)

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

            selectsql = "select * from contact where IMEI = '%s' and number = '%s' "%(IMEI,number)
            cur.execute(selectsql)
            print("rowcount is ",cur.rowcount)
            if cur.rowcount > 0:
                updatesql = "update contact set contact_name = '%s' where IMEI = '%s' and number = '%s' " \
                            %(name,IMEI,number)
                try:
                    cur.execute(updatesql)
                    db.commit()
                except:
                    db.rollback()
            else:
                insertsql = "insert into contact(IMEI,contact_name,number) values" \
                            "('%s','%s','%s')" %(IMEI,name,number)
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
    selectsql = "select * from message where IMEI = '%s' and contact_number = '%s' " \
                "and type = '%s' and date = '%s'"%(IMEI,number,message_type,date)
    cur.execute(selectsql)

    if cur.rowcount == 0:
        insertsql = "insert into message(IMEI,contact_name,contact_number,type,date,body) values" \
                    "('%s','%s','%s','%s','%s','%s')" % (IMEI, person, number,message_type,date,body)

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
