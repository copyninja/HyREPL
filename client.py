import socket
import sys
import threading
import time
from nrepl.bencode import encode, decode


ip = '127.0.0.1'
port = 9999

def client(ip, port, message):
    msg = bytes(encode(message), 'utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    asd = True
    try:
        sock.sendall(msg)
        while asd == True:
            response = str(sock.recv(2048), 'utf-8')
            if response:
                for i in decode(response):
                    print(i)
    except KeyboardInterrupt:
        sock.shutdown()
        del sock


#client(ip, port, {"op": "eval", "code": '(def b 2)'})
#client(ip, port, {"op": "eval", "code": '(+ 2 b)'})
a = threading.Thread(target=client, args=(ip, port, {"op": "eval", "code": '(def a (input))'}))
a.start()
time.sleep(2)
del a
b = threading.Thread(target=client, args=(ip,port, {"op": "stdin", "value": "test"}))
b.start()
time.sleep(2)
del b
c = threading.Thread(target=client, args=(ip,port, {"op": "eval", "code": "(print a)"}))
c.start()
time.sleep(2)
del c
