import re
import InputStream

class Token():
	def __init__(self, type, lexme, line, col):
		self.type = type
		self.lexme = lexme
		self.line = line
		self.col = col
	def __str__(self):
		return self.type+" : "+self.lexme
class Lexer():
	def __init__(self,spec):
		self.shorthands = {}
		self.tokens = []
		self.file = None
		self.filePointer = -1
		self.line = 1
		self.col = 0
		self.importTokenSpec(spec)

	def setInputStream(self, file):
		f = open(file,'r')
		self.file = f.read()
		self.filePointer = 0
		f.close()

	def getNextToken(self):
		if self.file == None:
			raise Exception("To begin getting tokens first set a input stream")
		if self.filePointer >= len(self.file):
			return None
		currFile = self.file[self.filePointer:]
		for t in self.tokens:
			regex = "^"+t[0]
			s = re.search(regex,currFile)
			if s != None:
				lexme = s.group(0)
				tType = t[1]
				retToken = Token(tType,lexme,self.line,self.col)
				if(t[1] == "NEWLINE"):
					self.line+=1
					self.col = 0
				else:
					self.col += len(lexme)
				self.filePointer += len(lexme)
				return retToken
		# handle unknown token (might be in a comment, don't crash)
		# note we don't handle lines, currFile[self.filePointer] != NEWLINE
		# if it was the regex would catch it. 
		self.filePointer+=1
		self.col += 1
		return Token("UNKNOWN_TOKEN","UNKNOWN",self.line,self.col)


	def importTokenSpec(self,file):
		f = open(file,'r')
		lines = f.readlines()
		f.close()
		state = -1
		for line in lines:
			line = line.strip()
			if len(line) == 0:
				continue
			if line[0] == "%":
				# command
				if line[1:] == "shorthands":
					state = 2
				elif line[1:] == "tokens":
					state = 1
				else:
					raise Exception("Unknown Spec Command: '"+line[1:]+"'")
				continue
			if state == -1:
				continue
			elif state == 1:
				self.getT(line)
			elif state == 2:
				self.getSH(line)
	def processRegex(self,regex):
		final = regex
		shorthands = re.findall(r'{[^\{\}]*}',regex,re.IGNORECASE)
		if shorthands == None:
			return regex
		for shRaw in shorthands:
			sh = shRaw[1:-1]
			if sh in self.shorthands:
				final = re.sub(shRaw,self.shorthands[sh],final)
			else:
				raise Exception("unknown shorthand: '"+sh+"'")
		return final
	def getSH(self, line):
		args = re.sub(r'\t+','\t',line).split("\t")
		name = args[0]
		regex = self.processRegex(args[1])
		self.shorthands[name]=regex
	def getT(self, line):
		args = re.sub(r'\t+','\t',line).split("\t")
		if args[0][0] == '"':
			regex = re.escape(args[0][1:-1])
		else:
			regex = self.processRegex(args[0])
		name = args[1]
		self.tokens.append((regex,name))

if __name__ == "__main__":
	l = Lexer("specs/C_Tokens_Simple.txt")
	l.setInputStream("tests/test_basic.c")
	t = l.getNextToken()
	while t != None:
		t = l.getNextToken()
