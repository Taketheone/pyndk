# !/usr/bin/env python
# -*- coding:utf-8 -*-

import Queue
import threading
import time
import sys
import traceback
class CWorkerMgr(object):
    
    def init(self, maxNum=5000, threadNum=8, timeOut=30):
        self._workQueue = Queue.Queue(maxNum)
        self._threads = []
        self._timeOut = timeOut
        self.__initThreadPool(threadNum)

    """
             初始化线程
    """
    def __initThreadPool(self, threadNum):
        for i in range(threadNum):
            self._threads.append(CWorker(self._workQueue, self._timeOut))

    """
             添加一项工作入队
    """
    def addJob(self, callable, *args, **kwds):
        try:
            self._workQueue.put_nowait((callable, args, kwds))#任务入队，Queue内部实现了同步机制
            return True
        except:
            return False

class CWorker(threading.Thread):
    def __init__(self, workQueue, timeOut=20):
        
        threading.Thread.__init__(self)
        self._workQueue = workQueue
        self._timeOut = timeOut
        self.setDaemon(True)
        self.start()

    def run(self):
        #死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            try:
                #任务异步出队，Queue内部实现了同步机制
                callable, args, kwds = self._workQueue.get(self._timeOut)
                callable(*args, **kwds)
            except Queue.Empty: #任务队列空的时候结束此线程
                continue
            except:
                traceback.print_exc()
                continue


if __name__ == '__main__':
    #具体要做的任务
    def do_job(i, msg):
        m = i		
    start = time.time()
    manager = CWorkerMgr()
    manager.init(10000,8)
    for i in range(10000):    
        manager.addJob(do_job, i, 'abcd')    
    
    #work_manager.wait_allcomplete()
    end = time.time()
    print "cost all time: %s" % (end - start)
    time.sleep(10000)
