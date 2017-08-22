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
class Tokeniser():
	def __init__(self, filename):
		if filename == None:
			self.stream = None
		else:
			self.stream = InputStream(filename)
		self.complete = False
		self.LL0TokenMap = {
			# white space
			" ":("space",None,False),
			"	":("tab",None,False),
			"\n":("newLine",None,False),
			# braces/brackets
			"{":("openBrace",None,False),
			"}":("closeBrace",None,False),
			"(":("openBracket",None,False),
			")":("closeBracket",None,False),
			"[":("openSquareBracket",None,False),
			"]":("closeSquareBracket",None,False),
			# basic control
			";":("semicolon",None,False),
			",":("comma",None,False),
			# math
			"+":("mathSymbol",None,False),
			"-":("mathSymbol",None,False),
			"/":("mathSymbol",None,False),
			"*":("mathSymbol",None,False),
			">":("mathSymbol",None,False),
			"<":("mathSymbol",None,False),
			"=":("equals",None),
			"\"":("stringLiteral","\"",True),
			"'":("charLiteral","'",True),
			# special
			"$":("doller",None,False),
			"@":("at",None,False),
		}
		# token, lookahead -> token-type, terminating symbol, terminating symbol lookahead
		self.LL1TokenMap = {
			("/","/"):("comment","\n",None,False),
			("/","*"):("comment","*","/",True),
			("=","="):("mathSymbol",None,None,False),
			("if","("):("if",None,None,False),
			("if"," "):("if",None,None,False),
			("else","{"):("else",None,None,False),
			("else"," "):("else",None,None,False),
			("while","("):("while",None,None,False),
			("while"," "):("while",None,None,False),
			("for","("):("for",None,None,False),
			("for"," "):("for",None,None,False),
			("#include"," "):("include",'\n',None,False),
			("#define"," "):("define",'\n',None,False),
			("return"," "):("return",None,None,False),
			("void"," "):("primType",None,None,False),
			("char"," "):("primType",None,None,False),
			("short"," "):("primType",None,None,False),
			("int"," "):("primType",None,None,False),
			("long"," "):("primType",None,None,False),
			("float"," "):("primType",None,None,False),
			("double"," "):("primType",None,None,False),
			("signed"," "):("primType",None,None,False),
			("unsigned"," "):("primType",None,None,False),
			("struct"," "):("primType",None,None,False),
			("union"," "):("primType",None,None,False),
			("const"," "):("primType",None,None,False),
			("volatile"," "):("primType",None,None,False)
		}

	def LL1SkipUntil(self,stream,curr,s,inclTerminal):
		while stream.peek() != s:
			curr+= stream.getNext()
		if inclTerminal:
			curr += stream.getNext()
		return curr

	def LL2SkipUntil(self,stream,curr,s,n,inclTerminal):
		next = stream.getNext()
		while not (next == s and stream.peek() == n):
			curr += next
			next = stream.getNext()
		if inclTerminal:
			curr += next
			curr += stream.getNext()
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
					curr = self.LL1SkipUntil(stream,curr,tokenInfo[1],tokenInfo[2])
				else:
					curr = self.LL2SkipUntil(stream,curr,tokenInfo[1],tokenInfo[2],tokenInfo[3])
				return Token(tokenInfo[0],curr,stream.currLine,stream.lineIndex)

			# LL0 tokens
			if curr.lower() in self.LL0TokenMap:
				prev = curr.lower()
				if self.LL0TokenMap[curr.lower()][1] != None:
					curr = self.LL1SkipUntil(stream,curr,self.LL0TokenMap[prev][1],self.LL0TokenMap[prev][2])
				return Token(self.LL0TokenMap[prev][0],curr,stream.currLine,stream.lineIndex)

			# general token cases
			if not self.stream.hasNext():
				self.complete = True
			# literal token
			if re.match(r'\d+(\.\d*|\.)?',curr) and (stream.peek() == " " or stream.peek() == ";" or not stream.hasNext()):
				return Token("numberLiteral",curr,stream.currLine,stream.lineIndex)

			# identifiers
			if (currLookAhead[1] != None and not re.match(r'\w',currLookAhead[1])) or not stream.hasNext():
				return Token("identifier",curr,stream.currLine,stream.lineIndex)
		raise Exception("'"+curr+"' was not recognised as a token")