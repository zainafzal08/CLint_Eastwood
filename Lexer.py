import re
import InputStream

class Lexer():
	def __init__(self,spec):
		self.shorthands = {}
		self.tokens = []
		self.inputStream = None
		self.importTokenSpec(spec)
	def setInputStream(self, file):
		self.inputStream = InputStream.InputStream(file)
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
		shorthands = re.search(r'{([^\{\}]*)}',regex)
		if shorthands == None:
			return regex
		if shorthands is not list:
			shorthands = [shorthands]
		for sh in shorthands:
			if sh.group(1) in self.shorthands:
				final = re.sub(sh.group(0),self.shorthands[sh.group(1)],final)
			else:
				raise Exception("unknown shorthand: '"+sh.group(1)+"'")
		return final
	def getSH(self, line):
		args = re.sub(r'\t+','\t',line).split("\t")
		name = args[0]
		regex = self.processRegex(args[1])
		self.shorthands[name]=regex
	def getT(self, line):
		args = re.sub(r'\t+','\t',line).split("\t")
		if args[0][0] == '"':
			regex = args[0][1:-1]
		else:
			regex = self.processRegex(args[0])
		name = args[1]
		self.tokens.append((regex,name))
	def 


if __name__ == "__main__":
	l = Lexer("specs/C_Tokens_Simple.txt")
	l.setInputStream("tests/test_basic.c")
	print(l.tokens)