#0a - Send multiple data lines by open and closing a new socket each time
#0b - Attempt to reuse existing socket

import socket
import time

s = socket.socket()
host = 'localhost'
port = 1520
s.connect((host, port))
s.send(bytes('{"00:06:66:61:A9:59":[1,43,874,300,0,0,0,0],"00:06:66:61:A3:48":[1,299,605,250,0,0,0,0]}', 'UTF-8'))
time.sleep(1)
s.send(bytes('{"00:06:66:61:A9:59":[1,43,0,0,0,0,0,0],"00:06:66:61:A3:48":[1,299,0,0,0,0,0,0]}', 'UTF-8'))
s.close()
