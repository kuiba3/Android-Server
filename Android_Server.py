from socketserver import (TCPServer as TCP,StreamRequestHandler as SRH)
from time import ctime

HOST = ''
PORT = 6543

ADDR = (HOST, PORT)

class MyRequestHandler(SRH):
    def handle(self):
        ## 获取数据的种类
        data_type = self.request.recv(1024).strip().decode()

        print('...connected from:', self.client_address, ctime())
        print('type is',data_type)

        if data_type != "keyword_message":
            data = self.request.recv(1024).strip().decode()
            datadict = eval(data)
            print(data)

        else:
            lengthstr = self.request.recv(1024).strip().decode()
            print(lengthstr)
            lengthdict = eval(lengthstr)
            length = lengthdict["length"]

            for i in range(0,length):
                data = self.request.recv(4 * 1024).strip().decode()
                datadict = eval(data)
                print(data)

        send_data = (data_type + str(" ok")).encode('utf-8')
        self.request.send(send_data)
        print("send OK :", send_data)




tcpServ = TCP(ADDR, MyRequestHandler)

print('waiting for connection...')
tcpServ.serve_forever()
