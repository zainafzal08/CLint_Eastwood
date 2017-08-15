class InputStream():
	def __init__(self, filepath):
		with open(filepath, 'r') as content_file:
			self.raw = content_file.read()
			self.data = list(self.raw)
			self.currIndex = 0;
			self.currLine = 1;
			self.lineIndex = 0;
			self.prev = None
	def getNext(self):
		if(self.currIndex < len(self.data)):
			if(self.prev == '\n'):
				self.currLine+=1
				self.lineIndex = 0
			ret = self.data[self.currIndex]
			self.prev = ret
			self.currIndex+=1
			self.lineIndex+=1
			return ret
	def hasNext(self):
		if self.currIndex < len(self.data):
			return True
		else:
			return False
	def isLast(self):
		if self.currIndex == len(self.data)-1:
			return True
		return False
	def peek(self):
		if self.currIndex < len(self.data):
			return self.data[self.currIndex]
		else:
			return None