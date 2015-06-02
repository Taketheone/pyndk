'''
Created on 2012-9-24

@author: Administrator
'''
from pyndk import CPackageFilter
from struct import *
class CH2T3PackageFilter(CPackageFilter.CPackageFilter):
    def __init__(self):
        pass
    def isWholePackage(self, inBuf):
        
        
        if len(inBuf) < 6:
            return -1;
        else:
            startBuff = inBuf[0:13]
            stx, length, cmd, seq = unpack('>BIHI', startBuff)
            endBuf = inBuf[length - 1:-1]
            etx = unpack('>B', endBuf)
            if etx == 3:
                return length
            else:
                return -2
