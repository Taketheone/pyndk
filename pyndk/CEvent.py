import select 
import heapq
import os
import Queue
import traceback
from pyndk import Utils

EV_DONE = 0
EV_READ = 1
EV_WRITE = 2

MAX_EPOLL_TIME_OUT = 1

class CEvent(object):
    
    def  __init__(self):
        self.epollHandler = select.epoll()
        self.fdEvents = {}
        self.timerHeap = []
        self.timerUnique = {}
        self.runFlag = True
        self.pipe = os.pipe()
        self.msgQueue = Queue.Queue(10000)
        
        self.addFdEvent(self.pipe[0], EV_READ, None, None)
        
    def addFdEvent(self, fd, mask, callback, data):
        
        ctrl = False
        if self.fdEvents.has_key(fd):
            ctrl = True
        
        event = self.fdEvents.setdefault(fd, CEventData());
        event.mask = event.mask | mask
        evMask = event.mask;
        
        if mask & EV_READ:
            event.onRead = callback
            event.rdata = data
        if mask & EV_WRITE:
            event.onWrite = callback
            event.wdata = data
        epollMask = 0
        if evMask & EV_READ:
            epollMask |= select.EPOLLIN
        if evMask & EV_WRITE:
            epollMask |= select.EPOLLOUT

        if ctrl:
            self.epollHandler.modify(fd, epollMask)
        else:
            self.epollHandler.register(fd, epollMask)
            
        return True;
             
    def delFdEvent(self, fd, mask):
        if self.fdEvents.has_key(fd):
            event = self.fdEvents[fd]; 
            event.mask = event.mask & (~mask)
            evMask = event.mask;
            epollMask = 0
            
            if evMask & EV_READ:
                epollMask |= select.EPOLLIN
            if evMask & EV_WRITE:
                epollMask |= select.EPOLLOUT
                
            if event.mask == EV_DONE:
                self.fdEvents.pop(fd)
                self.epollHandler.unregister(fd)
            else:
                self.epollHandler.modify(fd, epollMask)

    def addMessage(self, callable, *args, **kwds):
        
        self.msgQueue.put_nowait((callable, args, kwds))
        
        os.write(self.pipe[1], '1')
        
        
    def addTimer(self, timerId, expire, callback, data):
        
        timeNow = Utils.timeNow()
        expire = timeNow + expire
        if self.timerUnique.has_key(timerId):
            self.delTimer(timerId)
        heapq.heappush(self.timerHeap, [expire, timerId, callback, data])
        self.timerUnique[timerId] = None
       
    def delTimer(self, timerId):
        for item in self.timerHeap:
            if item[1] == timerId:
                self.timerHeap.remove(item)
                self.timerUnique.pop(timerId)
                break
   
    def run(self):
        while self.runFlag:
            try:
                timeNow = Utils.timeNow() 
                expire = MAX_EPOLL_TIME_OUT
                while True:
                    if len(self.timerHeap) == 0 :
                        break
                    timer = heapq.nsmallest(1, self.timerHeap)[0]
    
                    
                    if timer[0] <= timeNow:
                        self.timerHeap.remove(timer)
                        self.timerUnique.pop(timer[1])
                        
                        if timer[2]:
                            timer[2](timer[1], timer[3])
                    else:
                        expire = (timer[0] - timeNow) / 1000.00  
                        break
                          
        
                epollEvents = self.epollHandler.poll(expire)

                for epollEvent in epollEvents:
                    if epollEvent[1] & select.EPOLLIN or epollEvent[1] & select.EPOLLERR or epollEvent[1] & select.EPOLLHUP:
                        
                        # for event message
                        if epollEvent[0] == self.pipe[0]:
                            
                            os.read(epollEvent[0], 1) 
                            callable, args, kwds = self.msgQueue.get_nowait()
                            callable(*args, **kwds) 
                            self.msgQueue.task_done()
                            
                        else:
                            if self.fdEvents[epollEvent[0]].onRead:
                                self.fdEvents[epollEvent[0]].onRead(epollEvent[0], self.fdEvents[epollEvent[0]].rdata)
                    
                    if (epollEvent[1] & select.EPOLLOUT):
                        if self.fdEvents[epollEvent[0]].onWrite:
                            self.fdEvents[epollEvent[0]].onWrite(epollEvent[0], self.fdEvents[epollEvent[0]].wdata)
            except Exception as e:
                traceback.print_exc()
                continue
            
    def stop(self):
        self.runFlag = False


class CEventData(object):
    def __init__(self):
        self.rdata = None
        self.wdata = None
        self.onRead = None
        self.onWrite = None
        self.mask = 0
