'''
@author: jiangyouxing
'''
class CCircleQueue(object):
    
    def __init__(self,queueSize = 10000):
        self._data = [ x for x in range(queueSize) ]
        self._front = 0;
        self._rear = 0;
        self._size = queueSize;
    def push(self,item):
        if self.full():
            return False
        self._data[self._rear] = item
        self._rear = (self._rear+1) % self._size
        return True
    def pop(self):
        if self.empty():
            return None
        item = self._data[self._front]
        self._front = (self._front+1) % self._size
        return item
    def empty(self):
        return self._front == self._rear
    def full(self):
        return ((self._rear+1)%self._size) == self._front
    
    
    
if __name__ == '__main__':
    queue = CCircleQueue(10000)
    for i in range(10000):
        queue.push('11'+str(i))
    print queue.pop()
    print queue.pop()
    
    
    