from Lexer import Lexer
import re

class Grammar():
	def __init__(self,tokens,spec):
		self.tokens = tokens
		self.transformations = {}
		self.root = None
		self.selectSet = {}
		self.firstSetsFound = []
		self.followSetsFound = []
		self.importSpec(spec)

	def showTokens(self):
		for t in self.tokens:
			print(t)

	def show(self,req):
		if(req == "transformations"):
			for trs in sorted(self.transformations):
				print(trs+" -> "+self.transformations[trs][0])
				for option in self.transformations[trs][1:]:
					print("    |"+option)
		elif(req == "select sets"):
			for trs in sorted(self.selectSet):
				print(trs)
				print("    "+str(self.selectSet[trs]))

	def importSpec(self, file):
		f = open(file,'r')
		content = f.read()
		f.close()
		# clean the file and make it into a set of
		# transforations seperated by a special char '$'
		content = content.replace('\n','')
		content = re.sub(r'\s+',' ',content)
		content = re.sub(r'[^\'];','$',content)
		transformations = content.split("$")
		
		# add each to the grammer transformation set
		for i,trs in enumerate(transformations):
			trs = trs.strip()
			if(len(trs) == 0):
				continue
			# regex extract mess
			trs = re.sub(r'[^\']\:','$',trs)
			name = trs.split("$")[0].strip().lower()
			optionsRaw = trs.split("$")[1]
			optionsRaw = re.sub(r'[^\']\|','$',optionsRaw)
			optionsRaw = optionsRaw.split("$")
			options = list(map(lambda x: x.strip().lower(),optionsRaw))

			self.transformations[name] = options
			if i == 0:
				self.root = name
		# set up select set map
		for term in self.transformations:
			self.selectSet[term] = self.getSelectSet(term)

	# no idea how to do this
	def epsilon(self, term):
		return False

	# make less ugly lmao
	def getFirstSet(self, trs):
		result = set()
		if trs in self.firstSetsFound:
			return result
		else:
			self.firstSetsFound.append(trs)
		for option in self.transformations[trs]:
			for term in option.split(" "):
				if term in self.tokens:
					result.add(term)
					break
				elif not self.epsilon(term):
					result |= self.getFirstSet(term)
					break
				else:
					result |= self.getFirstSet(term)
		return result

	# in desperate need of a refactor
	def getFollowSet(self, trs):
		result = set()
		if trs in self.followSetsFound:
			return result
		else:
			self.followSetsFound.append(trs)
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
							j+=1
						# check if we ran off the end
						if j == len(optionList):
							result |= self.getFollowSet(trs)
		return result

	def getSelectSet(self, transformation):
		result = set()
		self.firstSetsFound = []
		result |= self.getFirstSet(transformation)
		if self.epsilon(transformation):
			self.followSetsFound = []
			result |= self.getFollowSet(transformation)
		return result


if __name__ == "__main__":
	# run the parser/lexer
	l = Lexer("specs/C_Tokens_Simple.txt")
	l.setInputStream("tests/test_basic.c")
	grammar = Grammar(l.getTokenList(),"specs/C_Grammar_Simple.txt")
	grammar.show("select sets")