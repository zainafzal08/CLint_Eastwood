from InputStream import InputStream
import re

class Token():
	def __init__ (self,tokType,lex,line,char):
		self.type = tokType
		self.lexme = lex
		self.line = line
		self.char = char
	def show(self):
		if self.lexme != '\n':
			print(self.type + " : "+self.lexme)
		else :
			print(self.type + " : \\n")

# TODO: line/index for multi line comments is a bit fucked yo. 
# TODO: tokeniser assumes #define and #import end with new lines
# 
class Tokeniser():
	def __init__(self, filename):
		self.stream = InputStream(filename)
		self.complete = False
		self.LL0TokenMap = {
			# white space
			" ":("space",None),
			"	":("tab",None),
			"\n":("newLine",None),
			# braces/brackets
			"{":("openBrace",None),
			"}":("closeBrace",None),
			"(":("openBracket",None),
			")":("closeBracket",None),
			"[":("openSquareBracket",None),
			"]":("closeSquareBracket",None),
			# basic control
			";":("semicolon",None),
			",":("comma",None),
			# math
			"+":("mathSymbol",None),
			"-":("mathSymbol",None),
			"/":("mathSymbol",None),
			"*":("mathSymbol",None),
			">":("mathSymbol",None),
			"<":("mathSymbol",None),
			"=":("equals",None),
			"\"":("stringLiteral","\""),
			"'":("charLiteral","'")
		}
		# token, lookahead -> token-type, terminating symbol, terminating symbol lookahead
		self.LL1TokenMap = {
			("/","/"):("comment","\n",None),
			("/","*"):("comment","*","/"),
			("=","="):("mathSymbol",None,None),
			("if","("):("if",None,None),
			("if"," "):("if",None,None),
			("else","{"):("else",None,None),
			("else"," "):("else",None,None),
			("while","("):("while",None,None),
			("while"," "):("while",None,None),
			("for","("):("for",None,None),
			("for"," "):("for",None,None),
			("#include"," "):("include",'\n',None),
			("#define"," "):("define",'\n',None),
			("return"," "):("return",None,None),
			("void"," "):("primType",None,None),
			("char"," "):("primType",None,None),
			("short"," "):("primType",None,None),
			("int"," "):("primType",None,None),
			("long"," "):("primType",None,None),
			("float"," "):("primType",None,None),
			("double"," "):("primType",None,None),
			("signed"," "):("primType",None,None),
			("unsigned"," "):("primType",None,None),
			("struct"," "):("primType",None,None),
			("union"," "):("primType",None,None),
			("const"," "):("primType",None,None),
			("volatile"," "):("primType",None,None)
		}

	def LL1SkipUntil(self,stream,curr,s):
		while stream.peek() != s:
			curr+= stream.getNext()
		stream.getNext()
		return curr

	def LL2SkipUntil(self,stream,curr,s,n):
		next = stream.getNext()
		while not (next == s and stream.peek() == n):
			curr += next
			next = stream.getNext()
		stream.getNext()
		return curr

	def getToken(self):
		if self.stream.isLast() == True:
			self.complete = True
		stream = self.stream
		curr = ""
		while stream.hasNext():
			# get next char
			curr += stream.getNext()
			currLookAhead = (curr.lower(),stream.peek())

			# LL1 tokens
			if currLookAhead[1] != None and currLookAhead in self.LL1TokenMap:
				tokenInfo = self.LL1TokenMap[currLookAhead]
				if tokenInfo[1] == None:
					pass
				elif tokenInfo[2] == None:
					curr = self.LL1SkipUntil(stream,curr,tokenInfo[1])
				else:
					curr = self.LL2SkipUntil(stream,curr,tokenInfo[1],tokenInfo[2])
				return Token(tokenInfo[0],curr,stream.currLine,stream.lineIndex)

			# LL0 tokens
			if curr.lower() in self.LL0TokenMap:
				prev = curr.lower()
				if self.LL0TokenMap[curr.lower()][1] != None:
					curr = self.LL1SkipUntil(stream,curr,self.LL0TokenMap[prev][1])
				return Token(self.LL0TokenMap[prev][0],curr,stream.currLine,stream.lineIndex)

			# general token cases
			# literal token
			if re.match(r'\d+(\.\d*|\.)?',curr) and (stream.peek() == " " or stream.peek() == ";"):
				return Token("numberLiteral",curr,stream.currLine,stream.lineIndex)

			# identifiers
			if currLookAhead[1] != None and not re.match(r'\w',currLookAhead[1]):
				return Token("identifier",curr,stream.currLine,stream.lineIndex)
		raise Exception("'"+curr+"' was not recognised as a token")