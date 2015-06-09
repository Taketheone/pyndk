# pyndk 
python 高性能,高并发，轻量级，多进程，多线程，异步非阻塞网络开发框架。适用linux 下 python 2.6-2.7版本（不能用于windows，因为用了select.epoll ) 4w/qps
===============================
        from pyndk.CCommMgr import *
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
             #收到完整包会调用此函数     
            def onRead(self, session, package): 
                response = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello"
                CCommMgr.getInstance().write(session,response,True);
            #客户端连接时会调些函数    
            def onConn(self, session, flag): 
                pass
                #print 'onConn'
            #客户端连接断掉会调用此函数    
            def onClose(self, session): 
                #print 'onClose'
                pass
             #网络IO出错会调用此函数    
            def onError(self, msg):
                print ('onError')
              #记时器回调  
            def onTimer(self, timerId, data): #
                print 'onTimer'
                CCommMgr.getInstance().setTimer(1, 1000, self, data)
                
        if __name__ == '__main__':
            #创建服务，监听9003端口，包过滤器为 CRawPackageFilter（用来关定包的完整性）
            srvId1 = CCommMgr.getInstance().createSrv(SRV_TCP, '0.0.0.0', 9003, CRawPackageFilter())
            #初始化处理器
            ProCenter.getInstance().init()
            #指定服务处理器
            CCommMgr.getInstance().setProcessor(srvId1, ProCenter.getInstance())
            #设置记时器处理器
            CCommMgr.getInstance().setTimer(1, 1000, ProCenter.getInstance(), None)
            #以单进程epoll事件模型启动服务
            #CCommMgr.getInstance().start() single process the better performance and worst concurrency
            #以多进程模epoll 事件模型启动服务
            CCommMgr.getInstance().fork(4) #multi process the better performance and better concurrency

