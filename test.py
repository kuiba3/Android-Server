import pymysql

data = {'IMEI': '863952036392072', '0': {'副营长': '13755132542'}, '1': {'马班长': '13874811864'}}
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

if __name__ == '__main__':
    '''db = pymysql.connect("localhost","root","12345","server")
    cur = db.cursor()
    try:
        cur.execute("delete from app")
        db.commit()
    except:
        db.rollback()'''

    Contact(data)
    pass