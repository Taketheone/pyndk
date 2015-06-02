'''
@author: jiangyouxing
'''
class CProcessor(object):
	def onRead(self, session, package):
		raise RuntimeError("not implement onRead")
	def onWork(self,session,package):
		raise RuntimeError("not implement onWork")
	def onUdpRead(self, session, package):
		raise RuntimeError("not implement onUdpRead")
	def onConn(self, session, flag):
		raise RuntimeError("not implement onConn")
	def onClose(self, session):
		raise RuntimeError("not implement onClose")
	def onMessage(self, type, data):
		raise RuntimeError("not implement onMessage")
	def onError(self, msg):
		raise RuntimeError("not implement onError")
	def onTimer(self, timerId, data):
		raise RuntimeError("not implement onTimer")