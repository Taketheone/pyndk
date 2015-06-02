'''
Created on 2012-9-21

@author: starjiang
'''
from socket import *
from pyndk.CEvent import *


event = CEvent()
session = {}


def onRead(fd, data):
    conn = session[fd]
    recvBuf = conn.recv(4096)
    
    if len(recvBuf) == 0:
        return 
    response = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello" 
    conn.send(response)
    event.delFdEvent(fd, EV_READ | EV_WRITE)
    conn.close()
    
def onWrite(fd, data):
    conn = session[fd]

    event.delFdEvent(fd, EV_WRITE)

def onAccept(fd, data):
    sock = data
    conn, addr = sock.accept()
    session[conn.fileno()] = conn
    conn.setblocking(False)
    conn.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    event.addFdEvent(conn.fileno(), EV_READ, onRead, conn)
    
def onTimer(timerId, data):
    print "onTimer"
    event.addTimer(1, 10000, onTimer, None)

serverFd = socket(AF_INET, SOCK_STREAM)

serverFd.setblocking(False) 
serverFd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

serverFd.bind(('127.0.0.1', 9003))

serverFd.listen(1024)
print "start 127.0.0.1:9003"

event.addFdEvent(serverFd.fileno(), EV_READ, onAccept, serverFd)
event.run()
