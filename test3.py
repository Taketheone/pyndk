'''
Created on 2012-9-24

@author: starjiang
'''
from pyndk.CCommMgr import *
from pyndk.CH2T3PackageFilter import CH2T3PackageFilter
from pyndk.CRawPackageFilter import CRawPackageFilter
from pyndk.CThreadPool import CThreadPool
from pyndk.CProcessor import CProcessor
import multiprocessing
import os
from pyndk.CWorkerMgr import CWorkerMgr

class ProCenter(CProcessor):
    
    instance = None
        
    @staticmethod
    def getInstance():
        if ProCenter.instance == None:
            ProCenter.instance = ProCenter()
        return ProCenter.instance
    def __init__(self):
        self.workpool = None;

    def init(self):  

        self.workpool = CWorkerMgr()
        self.workpool.init()
            
    def onRead(self, session, package):
        self.workpool.addJob(self.onWork(session, package))
        
    def onWork(self,session,package):
        CCommMgr.getInstance().addMessage(self,0,session)

    def onConn(self, session, flag):
        pass
        #print 'onConn'
        
    def onClose(self, session):
        #print 'onClose'
        pass
    def onMessage(self, type, data):
        response = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello"
        CCommMgr.getInstance().write(data,response,True);
    def onError(self, msg):
        print ('onError')
        
    def onTimer(self, timerId, data):
        print 'onTimer'
        CCommMgr.getInstance().setTimer(1, 1000, self, data)
        
if __name__ == '__main__':
    
    srvId1 = CCommMgr.getInstance().createSrv(SRV_TCP, '0.0.0.0', 9003, CRawPackageFilter())
    ProCenter.getInstance().init()
    CCommMgr.getInstance().setProcessor(srvId1, ProCenter.getInstance())
    CCommMgr.getInstance().setTimer(1, 1000, ProCenter.getInstance(), None)
    #CCommMgr.getInstance().start() single process,multi thread the worst performance and better concurrency
    CCommMgr.getInstance().fork(4) #multi process,multi thread the best performance and the best concurrency
    
    


