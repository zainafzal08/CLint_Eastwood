class Grammar():
	def __init__(self,tokens,spec):
		self.tokens = tokens
		self.transformations = {}
		self.root = None
		self.importSpec(spec)
		self.selectSet = {}
	def showTokens(self):
		for t in self.tokens:
			print(t)

	def importSpec(self, file):
		f = open(file,'r')
		content = f.read()
		f.close()
		# clean the file and make it into a set of
		# transforatiosn seperated by a special char '$'
		content = content.replace('\n','')
		content = re.sub(r'\s+',' ',content)
		content = re.sub(r'[^\'];','$',content)
		transformations = content.split("$")
		
		# add each to the grammer transformation set
		for i,trs in enumerate(transformations):
			trs = trs.strip()
			if(len(trs) == 0):
				continue
			name = trs.split(":")[0].strip().lower()
			options = list(map(lambda x: x.strip().lower(), trs.split(":")[1].split("|")))
			self.transformations[name] = options
			if i == 0:
				self.root = name
		# set up select set map
		for term in self.transformations:
			self.selectSet[term] = self.getSelectSet(term)

	# no idea how to do this
	def epsilon(self, term):
		return False

	def getFirstSet(self, trs):
		result = Set()
		for option in self.transformations[trs]:
			for term in option.split(" "):
				if term in self.tokens:
					result.add(term)
					break
				elif not epsilon(term):
					result |= self.getFirstSet(term)
					break
				else:
					result |= self.getFirstSet(term)
		return result

	# in desperate need of a refactor
	def getFollowSet(self, trs):
		result = Set()
		for trs in self.transformations:
			for option in self.transformations[trs]:
				optionList = option.split(" ")
				for i,term in enumerate(optionList):
					# found the term
					if term == trs:
						# get what comes after
						j = i+1
						while j < len(optionList):
							if optionList[j] in self.tokens:
								result.add(optionList[j])
								break
							else:
								result |= self.getFollowSet(optionList[j])
							if not self.epsilon(optionList[j]):
								break
							j++
						# check if we ran off the end
						if j == len(optionList):
							result |= self.getFollowSet(trs)
		return result

	def getSelectSet(self, transformation):
		result =Set()
		result |= self.getFirstSet(transformation)
		if self.epsilon(transformation):
			result |= self.getFollowSet(transformation)
		return result

	def getFirstSet(self, transformation):
		pass
	def getFollowSet(self, transformation):
		pass

if __name__ == "__main__":
	# run the parser/lexer
	l = Lexer("specs/C_Tokens_Simple.txt")
	l.setInputStream("tests/test_basic.c")
	grammar = Grammar(l.getTokenList(),"specs/C_Grammar_Simple.txt")
	