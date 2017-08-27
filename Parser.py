from Lexer import Lexer
from Lexer import Token
import re

class Grammar():
	def __init__(self,tokens):
		self.tokens = tokens
		self.transformations = {}
		self.firstSets = {}
		pass
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
		for trs in transformations:
			trs = trs.strip()
			if(len(trs) == 0):
				continue
			name = trs.split(":")[0].strip().lower()
			options = list(map(lambda x: x.strip().lower(), trs.split(":")[1].split("|")))
			self.transformations[name] = options
		# now get all the first sets
		for trs in self.transformations.keys():
			bootstrapPath = set()
			bootstrapPath.add(trs)
			self.firstSets[trs] = self.getFirstSet(self.transformations[trs],bootstrapPath)
	def getFirstSet(self,options,path):
		result = set()
		for option in options:
			term = option.split(" ")[0]
			if term in path:
				continue
			if term[0] == "'" or term in self.tokens:
				result.add(term)
			else:
				pathCpy = path.copy()
				pathCpy.add(term)
				result |= self.getFirstSet(self.transformations[term],pathCpy)
		return result

class Parser():
	def __init__(self, spec, tokens):
		self.grammar = Grammar(tokens)
		self.grammar.importSpec(spec)
		pass
	def parse():
		pass

if __name__ == "__main__":
	l = Lexer("specs/C_Tokens_Simple.txt")
	tknList = l.getTokenList()
	p = Parser("specs/C_Grammar_Simple.txt",tknList)
	l.setInputStream("tests/test_basic.c")
