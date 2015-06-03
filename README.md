# pyndk
python 高性能,高并发，轻量级，多进程，多线程网络开发框架
===============================
        from pyndk.CCommMgr import *
        from pyndk.CH2T3PackageFilter import CH2T3PackageFilter
        from pyndk.CRawPackageFilter import CRawPackageFilter
        from pyndk.CProcessor import CProcessor

        class ProCenter(CProcessor):
            instance = None
        
            @staticmethod
            def getInstance():
                if ProCenter.instance == None:
                    ProCenter.instance = ProCenter()
                return ProCenter.instance
            def __init__(self):
                pass
            def init(self):  
                pass
                  
            def onRead(self, session, package):
                response = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello"
                CCommMgr.getInstance().write(session,response,True);
            def onConn(self, session, flag):
                pass
                #print 'onConn'
                
            def onClose(self, session):
                #print 'onClose'
                pass
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
            #CCommMgr.getInstance().start() single process the better performance and worst concurrency
            CCommMgr.getInstance().fork(4) #multi process the better performance and better concurrency

