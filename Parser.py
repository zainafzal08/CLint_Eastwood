from Lexer import Lexer
from Lexer import Token
from Tree import Tree
import re
import logging, sys
from Grammar import Grammar


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
			elif t.type in self.grammar.selectSet[term]:
				return option
		raise Exception("Attempt to decend into "+trans+ " failed due to match failure on "+t.type)

	# useful function for skipping white space
	# it'll be ignored for enforcing the grammar BUT
	# still be in the ast. 
	def nextToken(self):
		t = self.lexer.getNextToken()
		while self.isWhiteSpace(t):
			self.tree.addTerminal(t)
			t = self.lexer.getNextToken()
		return t

	def isWhiteSpace(self, t):
		if t.type == "space":
			return True
		elif t.type == "newline":
			return True
		elif t.type == "tab":
			return True
		elif t.type == "vtab":
			return True
		return False

	def isCompilerTag(self,t):
		if t.type == "include":
			return True
		elif t.type == "define":
			return True
		return False


	def parse(self):
		# need to do
		pass

if __name__ == "__main__":
	# turn debugging on/off
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

	# run the parser/lexer
	l = Lexer("specs/C_Tokens_Simple.txt")
	l.setInputStream("tests/test_basic.c")
	p = Parser("specs/C_Grammar_Simple.txt",l)


