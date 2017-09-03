from Lexer import Lexer
from Lexer import Token
from Tree import Tree
import re

class Grammar():
	def __init__(self,tokens,spec):
		self.tokens = tokens
		self.transformations = {}
		self.firstSets = {}
		self.root = None
		self.importSpec(spec)

	def showFirstSets(self):
		for k in sorted(self.firstSets):
			print(k)
			for o in self.firstSets[k]:
				print("    "+o)

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
	def __init__(self, spec, l):
		self.grammar = Grammar(l.getTokenList(),spec)
		self.lexer = l
		self.tree = Tree()
	# given a transformation and a token, return the 
	# transformation that should be taken
	def collapseOptions(self, trans, t):
		for option in self.grammar.transformations[trans]:
			term = option.split(" ")[0]
			if term in self.grammar.tokens and t.type == term:
				return option
			elif term in self.grammar.tokens and t.type != term:
				continue
			elif t.type in self.grammar.firstSets[term]:
				return option
		raise Exception("Syntax error :/")

	# decend into a given transformation
	# updating the tree and terminating automatically
	def decend(self, trans, t):
		print("Decending into "+trans)
		option = self.collapseOptions(trans,t)
		print("    Collapsing into "+option)
		for term in option.split(" "):
			if term in self.grammar.tokens and term == t.type:
				self.tree.addTerminal(t)
				t = self.lexer.getNextToken()
			elif term in self.grammar.tokens and term != t.type:
				raise Exception("unexpected token "+t.type)
			else:
				prev = self.tree.curr
				self.tree.addTrans(term)
				t = self.decend(term,t)
				self.tree.curr = prev
		return t;

	def parse(self,root):
		self.tree.addTrans(root)
		t = self.lexer.getNextToken()
		self.decend(root,t)

if __name__ == "__main__":
	l = Lexer("specs/C_Tokens_Simple.txt")
	l.setInputStream("tests/test_basic.c")
	p = Parser("specs/C_Grammar_Simple.txt",l)
	p.parse("primary_expression")


