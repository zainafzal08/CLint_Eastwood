from Lexer import Lexer
from Lexer import Token
from Tree import Tree
import re
import logging, sys



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
		raise Exception("Attempt to decend into "+trans+ " failed due to match failure on "+t.type)

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
	# decend into a given transformation
	# updating the tree and terminating automatically
	def decend(self, trans, t):
		logging.debug(" Decending into "+trans)
		option = self.collapseOptions(trans,t)
		logging.debug("    Collapsing into "+option)
		for term in option.split(" "):
			if term in self.grammar.tokens and term == t.type:
				logging.debug("    accepting "+t.type)
				self.tree.addTerminal(t)
				t = self.nextToken()
			elif term in self.grammar.tokens and term != t.type:
				raise Exception("unexpected token "+t.type + " needed "+term)
			else:
				prev = self.tree.curr
				self.tree.addTrans(term)
				t = self.decend(term,t)
				self.tree.curr = prev
		return t;

	def isCompilerTag(self,t):
		if t.type == "include":
			return True
		elif t.type == "define":
			return True
		return False

	def handleCompilerTag(self,t):
		logging.debug("    ...Recognised Compiler Tag")
		line = []
		while t.type != "newline":
			line.append(t)
			t = l.getNextToken()
		line.append(t)
		self.compilerTags.append(line)
		t = self.nextToken()
		return t

	def handleComment(self,t):
		logging.debug("    ...Recognised Comment")
		comment = []
		while t.type != "commentend":
			comment.append(t)
			t = l.getNextToken()
		comment.append(t)
		self.comments.append(comment)
		t = self.nextToken()
		return t

	def parse(self):
		t = self.nextToken()
		# once this returns, keep decending into the next
		# valid transformation until finished
		while t != None:
			if self.isCompilerTag(t):
				t = self.handleCompilerTag(t)
				continue
			if t.type == "commentstart":
				t = self.handleComment(t)
				continue
			nextTrans = None
			logging.debug(" Look for next transformation for "+t.type)
			for trans in self.grammar.transformations:
				logging.debug("    ..."+trans)
				if t.type in self.grammar.firstSets[trans]:
					nextTrans = trans
					break
			if nextTrans == None:
				raise Exception("No transformation found for "+t.type)
			t = self.decend(nextTrans,t)

if __name__ == "__main__":
	# turn debugging on/off
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

	# run the parser/lexer
	l = Lexer("specs/C_Tokens_Simple.txt")
	l.setInputStream("tests/test_basic.c")
	p = Parser("specs/C_Grammar_Simple.txt",l)
	p.parse()


