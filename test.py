# coding: utf-8
import pymysql

data = {'number': '95588', 'person': '0', 'body': '【飞机火车免费升舱升座】恭喜您获得工银军魂信用卡权益领取资格，乘坐国内航班火车有机会免费升舱升座，微信关注“工银信用卡微讯”公众号，在“我要福利—我是持卡人—工银军魂信用卡”栏目点击领取，名额有限先到先得【爱购周末万家商户低至5折，爱购全球出国海淘最高21%返现，爱购扫码随机立减最高1000】【回复“esh”下载专属APP工银e生活】【线上客服微信关注“工银信用卡”服务号】工银信用卡【工商银行】', 'date': '2018-01-22 14:31:46', 'type': '1'}
IMEI = '863952036392072'
def database():
    db = pymysql.connect('localhost','root','12345','server')
    return db
def Contact(data):
    ## 获取IMEI的值
    IMEI = data['IMEI']

    ##连接数据库并获取连接对象
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
    print(selectsql)
    cur.execute(selectsql)

    if cur.rowcount == 0:
        insertsql = "insert into message(IMEI,contact_name,contact_number,type,date,body) values" \
                    "('%s','%s','%s','%s','%s','%s')" % (IMEI, person, number,message_type,date,body)

        print(insertsql)
        try:
            cur.execute(insertsql)
            db.commit()
        except:
            db.rollback()

    db.close()

if __name__ == '__main__':
    '''db = pymysql.connect("localhost","root","12345","server")
    cur = db.cursor()
    try:
        cur.execute("delete from app")
        db.commit()
    except:
        db.rollback()'''
    db = database()
    cur = db.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "select * from message where IMEI = {}".format('863952036392072')
    print(sql)
    cur.execute(sql)
    num = cur.rowcount
    print(num)
    for i in range(num):
        a = cur.fetchone()
        print(a)



    pass