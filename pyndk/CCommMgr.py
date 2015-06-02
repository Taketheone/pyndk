'''
Created on 2012-9-21

@author: Administrator
'''
import socket
import time
import traceback
from pyndk import CEvent
from errno import *
import sys
import os

SRV_TCP = 1
SRV_UDP = 2
CONN_TCP = 3



class CCommMgr(object):
    
    instance = None
    
    def __init__(self):
        self.event = None
        self.clients = {}
        self.servers = {}
        self.timers = {}
        
    @staticmethod
    def getInstance():  
        if CCommMgr.instance == None:
            CCommMgr.instance = CCommMgr() 
        return CCommMgr.instance
    
    def createSrv(self, srvType, ip, port, packageFilter):
        if srvType == SRV_TCP:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            server.setblocking(False) 
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((ip, port))
            server.listen(1024)
            
            serverInfo = CServer()
            
            serverInfo.obj = server
            serverInfo.type = srvType
            serverInfo.filter = packageFilter
            
            srvId = len(self.servers)
            
            self.servers[srvId] = serverInfo
            
            return srvId
        
        elif srvType == SRV_UDP:
            server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server.setblocking(False) 
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((ip, port))
            
            serverInfo = CServer()
            
            serverInfo.obj = server
            serverInfo.type = srvType
            serverInfo.filter = packageFilter
            
            srvId = len(self.servers)
            
            self.servers[srvId] = serverInfo
            
            return srvId
        
        return -1
    def setCallBack(self, srvId, onRead, onConn, onClose, onError):
        
        if self.servers.has_key(srvId):
            serverInfo = self.servers[srvId]
            serverInfo.onRead = onRead
            serverInfo.onConn = onConn
            serverInfo.onClose = onClose
            serverInfo.onError = onError
            return 0
        else:
            return -1
    def setProcessor(self,srvId,processor):
        if self.servers.has_key(srvId):
            serverInfo = self.servers[srvId]
            serverInfo.onRead = processor.onRead
            serverInfo.onConn = processor.onConn
            serverInfo.onClose = processor.onClose
            serverInfo.onError = processor.onError
            return 0
        else:
            return -1
    def createAsyncConn(self, srvType, packageFilter):
        
        if srvType == CONN_TCP:
            serverInfo = CServer()
     
            serverInfo.filter = packageFilter
            serverInfo.type = srvType
            srvId = len(self.servers)
            self.servers[srvId] = serverInfo
            return srvId
        
        return -1
    
    def connect(self, srvId, ip, port):
        
        client = CClient()
        client.srvId = srvId
        client.obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.obj.setblocking(False) 
        self.clients[client.obj.fileno()] = client
        
        serverInfo = self.servers[srvId]
        
        errno = client.obj.connect_ex((ip, port))

        if errno == 0:
            session = CSession()
            session.obj = client.obj
            session.addr = client.addr
            session.srvId = srvId 
            serverInfo.onConn(session, True)
            return 0
            
        if errno == EINPROGRESS:
            self.event.addFdEvent(client.obj.fileno(), CEvent.EV_WRITE, self.onConnect, client)
        else:
            serverInfo.onError('connect error %s,%s' % (ip, port))
            return -1
        return 0
        
    def setTimer(self, timerId, expire, processor, data):
        if self.event is None:
            self.timers[timerId] = (timerId, expire, processor.onTimer, data)
        else:
            self.event.addTimer(timerId, expire, processor.onTimer, data)
    def delTimer(self, timerId):
        if self.event is None:
            raise RuntimeError("server have not started, can not del timer")
        return self.event.delTimer(timerId)
    
    def addMessage(self, processor, *args, **kwds):
        if self.event is None:
            raise RuntimeError("server have not started, can not add message")
        return self.event.addMessage(processor.onMessage, *args, **kwds)
        
    def start(self):
        if self.event is None:
            self.event = CEvent.CEvent()
        for srvId, server in self.servers.iteritems():
            if server.type == SRV_TCP:
                self.event.addFdEvent(server.obj.fileno(), CEvent.EV_READ, self.onAccept, srvId)
            elif server.type == SRV_UDP:
                self.event.addFdEvent(server.obj.fileno(), CEvent.EV_READ, self.onUdpRead, srvId)
        for timer in self.timers.itervalues():
            self.event.addTimer(timer[0], timer[1], timer[2], timer[3])
            pass        
        return self.event.run()
    
    def fork(self,num):
        exit = 0
        for i in range(num):
            pid = os.fork()    
            if pid > 0:
                if i == (num-1):
                    
                    while 1:
                        info = os.wait()
                        print 'process',info[0],"exit"
                        exit+=1
                        if exit == num:
                            break

            else:
                self.start()
    
    def stop(self):
        return self.event.stop()
    
    def write(self, session, package, needClose):
        
        clientInfo = self.clients[session.obj.fileno()]
        clientInfo.needClose = needClose
        sendedLen = clientInfo.obj.send(package)
        
        if sendedLen < len(package):
            
            clientInfo.outBuf = package[sendedLen:len(package)]
            self.event.addFdEvent(clientInfo.obj.fileno(), CEvent.EV_WRITE, self.onWrite, clientInfo)
            
        elif sendedLen == len(package):
            if needClose:
                self.close(clientInfo.obj)    
            else:
                self.event.delFdEvent(clientInfo.obj.fileno(), CEvent.EV_WRITE)    
        return 0
    def writeTo(self, srvId, ip, port, package):
        if self.servers.has_key(srvId):
            serverInfo = self.servers[srvId]
            return serverInfo.obj.sendto(package, 0, (ip, port))
        else:
            return -1;
        
    def close(self, sock):
        
        self.clients.pop(sock.fileno())
        self.event.delFdEvent(sock.fileno(), CEvent.EV_READ | CEvent.EV_WRITE)
        sock.close()
            
    def onAccept(self, fd, data):

        serverInfo = self.servers[data]
        try:
            client = CClient()
            client.srvId = data
            client.obj, client.addr = serverInfo.obj.accept()
            self.clients[client.obj.fileno()] = client
            
            client.obj.setblocking(False)
            client.obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)            
            
            session = CSession()
            session.obj = client.obj
            session.addr = client.addr
            session.srvId = data 
            self.event.addFdEvent(client.obj.fileno(), CEvent.EV_READ, self.onTcpRead, client)
            serverInfo.onConn(session, True)
        except socket.error,e:
            errno, errmsg = e
            if errno != 11:
                serverInfo.onError("OnAccept:"+errmsg)
            
    def onConnect(self, fd, data):
        
        clientInfo = self.clients[fd]
        serverInfo = self.servers[clientInfo.srvId]
        
        self.event.delFdEvent(fd, CEvent.EV_WRITE)
        
        errno = clientInfo.obj.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR, 4)


        session = CSession()
        session.obj = clientInfo.obj
        session.srvId = clientInfo.srvId
            

        if errno == 0:    
            self.event.addFdEvent(fd, CEvent.EV_READ, self.onTcpRead, clientInfo) 
            serverInfo.onConn(session, True)
        else:
            serverInfo.onConn(session, False)
    
    def onWrite(self, fd, data):
        
        clientInfo = self.clients[fd]
        sendedLen = clientInfo.obj.send(clientInfo.outBuf)
        
        
        if sendedLen < len(clientInfo.outBuf):
            
            clientInfo.outBuf = clientInfo.outBuf[sendedLen:len(clientInfo.outBuf)]
        
        elif sendedLen == len(clientInfo.outBuf):
            if clientInfo.needClose:
                self.close(clientInfo.obj)
            else:
                self.event.delFdEvent(clientInfo.obj.fileno(), CEvent.EV_WRITE)
        
        
    def onTcpRead(self, fd, data):
        
        clientInfo = self.clients[fd]
        serverInfo = self.servers[clientInfo.srvId]
        
        try:
            inBuf = clientInfo.obj.recv(8192)
            
            if len(inBuf) == 0:
                session = CSession()
                session.srvId = clientInfo.srvId
                session.obj = clientInfo.obj
                session.addr = clientInfo.addr
                serverInfo.onClose(session)
                self.close(clientInfo.obj)
                return

            elif len(inBuf) > 0:
                clientInfo.inBuf += inBuf
                while True:
                    packLen = serverInfo.filter.isWholePackage(clientInfo.inBuf)
                    if packLen > 0:
                        session = CSession()
                        session.srvId = clientInfo.srvId
                        session.obj = clientInfo.obj
                        session.addr = clientInfo.addr
                        
                        package = clientInfo.inBuf[0:packLen]
                        
                        clientInfo.inBuf = clientInfo.inBuf[packLen:len(clientInfo.inBuf)]
                        serverInfo.onRead(session, package)
                    elif packLen == 0:
                        #package not ready
                        break
                    elif packLen == -1:
                        #package invalid
                        self.close(clientInfo.obj)
                        serverInfo.onError('onTcpRead invalid package')
                        
            else:
                self.close(clientInfo.obj)
                serverInfo.onError('onTcpRead recv data error')
        except IOError:
            traceback.print_exc()
            self.close(clientInfo.obj)
            serverInfo.onError('onTcpRead io exception')
        except:
            traceback.print_exc()
            serverInfo.onError('onTcpRead exception')
           
    def onUdpRead(self, fd, data):
        
        serverInfo = self.servers[data]
        try:
            inbuf, addr = serverInfo.obj.recvfrom(65535)
            
            packLen = serverInfo.filter.isWholePackage(inbuf)
            
            if packLen > 0:
                package = inbuf[0:packLen]
                session = CSession()
                session.obj = serverInfo.obj
                session.addr = addr
                session.srvId = data
                serverInfo.onRead(session, package)
            else:
                serverInfo.onError('onUdpRead invalid package')
        except:
            traceback.print_exc()
            serverInfo.onError('onUdpRead exception')

class CServer(object):
    def __init__(self):
        self.obj = None
        self.type = 0
        self.filter = None
        self.onRead = None
        self.onConn = None
        self.onClose = None
        self.onError = None
        self.ip = ''
        self.port = 0
        
class CClient(object):
    def __init__(self):
        self.srvId = 0
        self.obj = None
        self.addr = None 
        self.needClose = False
        self.inBuf = ''
        self.outBuf = ''
        
class CSession(object):
    def __init__(self):
        self.srvId = 0
        self.obj = None
        self.addr = None
        self.cTime = int(time.time())
