# !/usr/bin/env python
# -*- coding:utf-8 -*-
import threading
import time
import sys
import traceback
from CCircleQueue import CCircleQueue
class CThreadPool(object):
    
    def init(self, queueSize=10000, threadNum=8, timeOut=30):
        self._queueSize = queueSize
        self._threads = []
        self._timeOut = timeOut
        self.__initThreadPool(threadNum)
        self._seq = 0;
    """
             初始化线程
    """
    def __initThreadPool(self, threadNum):
        for i in range(threadNum):
            self._threads.append(CThread(i,self._queueSize, self._timeOut))

    """
             添加一项工作入队
    """
    def addJob(self, callable, *args, **kwds):
        self._seq = self._seq+1
        index = self._seq%len(self._threads)
        thread = self._threads[index]
        thread.addJob(callable, *args, **kwds)


class CThread(threading.Thread):
    def __init__(self, index ,queueSize = 10000, timeOut=20):
        
        threading.Thread.__init__(self)
        self._workQueue = CCircleQueue(queueSize)
        self._timeOut = timeOut
        self._index = index
        self.setDaemon(True)
        self.start()
    def addJob(self,callable, *args, **kwds):
        return self._workQueue.push((callable, args, kwds))
    def run(self):
        #死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            try:
                #任务异步出队，Queue内部实现了同步机制
                call = self._workQueue.pop()
                if call == None:
                    time.sleep(0.01)
                    continue
                callable = call[0]
                args = call[1]
                kwds = call[2]
                callable(*args, **kwds)

            except:
                traceback.print_exc()
                continue


if __name__ == '__main__':
    #具体要做的任务
    def do_job(i, msg):
        m = i		
    start = time.time()
    manager = CThreadPool()
    manager.init(10000,8)
    for i in range(10000):    
        manager.addJob(do_job, i, 'abcd')    
    
    #work_manager.wait_allcomplete()
    end = time.time()
    print "cost all time: %s" % (end - start)
    time.sleep(10000)
