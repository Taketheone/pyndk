'''
Created on 2012-9-24

@author: Administrator
'''
from pyndk import CPackageFilter

class CRawPackageFilter(CPackageFilter.CPackageFilter):
    def __init__(self):
        pass
    def isWholePackage(self, inBuf):
        return len(inBuf)

    
