import Tokeniser
from Tokeniser import Token
import sys
import os

class Rule():
	def __init__(self,tokenArray,ef,**kargs):
		self.tokenArray = tokenArray
		if self.tokenArray[-1] == None:
			raise Exception("You can not have a wildcard as a terminating token")
		self.expectedForm = ef
		self.reverse = False
		self.lexs = [None]*len(self.tokenArray)
		if "reverse" in kargs:
			self.reverse = kargs["reverse"]
		if "lexs" in kargs:
			self.lexs = kargs["lexs"]
			if len(self.lexs) != len(self.tokenArray):
				raise Exception("Supplied lexs array inconsistent with token array")

class Stylomatic():
	def __init__(self,indentWidth):
		self.rules = []
		self.indentWidth = indentWidth
		self.indentTriggers = {}
		self.failed = False
		self.filename = None
	def enforce(self,rule):
		self.rules.append(rule)
	def enforceIndent(self,tokenType,change):
		self.indentTriggers[tokenType] = change
	def check(self,filename,debug):
		self.filename = filename
		tokeniser = Tokeniser.Tokeniser(filename)
		indentWidth = self.indentWidth
		rawTokens = []
		while not tokeniser.complete:
			t = tokeniser.getToken()
			rawTokens.append(t)
			if(debug):
				t.show()
		# convert indentWidth spaces / tabs to indents
		i = 0
		tokens = []
		currIndentType = None
		while i < len(rawTokens)-indentWidth:
			token = rawTokens[i]
			if token.type == "tab":
				if currIndentType == None:
					currIndentType = "tab"
				elif currIndentType != "tab":
					self.raiseIndentFailure(token,"A Mix","Either All Tab Or All Space")
					return
				tokens.append(Token("indent",token.lexme,token.line,token.char))
			else:
				indnt = True
				for j in range(i,i+indentWidth):
					indnt = indnt and (rawTokens[j].type == "space")
				if indnt:
					if currIndentType == None:
						currIndentType = "space"
					elif currIndentType != "space":
						self.raiseIndentFailure(token,"A Mix","Either All Tab Or All Space")
						return
					tokens.append(Token("indent",token.lexme,token.line,token.char))
					i+=indentWidth-1
				else:
					tokens.append(token)
			i+=1

		for i in range(len(rawTokens)-indentWidth,len(rawTokens)):
			tokens.append(rawTokens[i])
		# enforce indenting
		self.enforceIndenting(tokens)
		# enforce rest of the rules
		for rule in self.rules:
			self.enforceRule(rule,tokens)
	def enforceIndenting(self,tokens):
		correctIndent = 0
		currIndent = 0
		expect = False
		for i,t in enumerate(tokens):
			if t.type in self.indentTriggers:
				correctIndent += self.indentTriggers[t.type]
			if(t.type == "newLine" and correctIndent > 0):
				expect = True
				currIndent = 0
				continue
			if(expect):
				if(currIndent == correctIndent):
					expect = False
					if(i+1 < len(tokens) and tokens[i+1].type == "indent"):
						self.raiseIndentFailure(t,currIndent+1,correctIndent)
				elif(t.type != "indent"):
					self.raiseIndentFailure(t,currIndent,correctIndent)
					expect = False
				else:
					currIndent+=1
	def enforceRule(self,rule, tokens):
		curr = 0
		for t in tokens:
			if curr == len(rule.tokenArray):
				if rule.reverse:
					self.raiseFailure(rule,t)
				curr = 0
			# wildcard
			if rule.tokenArray[curr] == None:
				if t.type == rule.tokenArray[curr+1]:
					curr+=1
				else:
					continue
			# take into accounts lexme if we care
			if t.type == rule.tokenArray[curr] and rule.lexs[curr] == None:
				curr+=1
			elif t.type == rule.tokenArray[curr] and rule.lexs[curr] != None and t.lexme == rule.lexs[curr]:
				curr+=1
			elif curr != 0:
				curr = 0
				if not rule.reverse:
					self.raiseFailure(rule,t)
	def raiseFailure(self,rule, t):
		self.failed = True
		print(self.filename+": Rule Failed @ line "+str(t.line)+": Expected "+rule.expectedForm)
	def raiseIndentFailure(self,t,curr,correct):
		self.failed = True
		print(self.filename+ ": Rule Failed @ line "+str(t.line)+": Expected "+str(correct)+" Indent(s) But Got "+str(curr))

if __name__ == "__main__":
	# indent width is enforced at 4
	styleomatic = Stylomatic(4)
	# what should trigger a indent/unindent
	styleomatic.enforceIndent("openBrace",1)
	styleomatic.enforceIndent("closeBrace",-1)
	# Rules
	# NOTE: None = wildcard i.e .* in regex sorta
	# NOTE: you can specify lexs for stuff like indentifiers

	rules = []
	rules.append(Rule(["if","space","openBracket"],"if<space>("))
	rules.append(Rule(["else","space","openBrace"],"else<space>{"))
	rules.append(Rule(["while","space","openBracket"],"while<space>("))
	rules.append(Rule(["for","space","openBracket"],"for<space>("))
	rules.append(Rule(["openBracket","space"],"No Space After A Open Bracket",reverse=True))
	rules.append(Rule(["space","closeBracket"],"No Space Before A Close Bracket",reverse=True))
	rules.append(Rule(["space","semicolon"],"No Space Before A Semicolon",reverse=True))
	rules.append(Rule(["identifier",None,"return","space","identifier"],"return EXIT_SUCCESS;",lexs=["main",None,None,None,"EXIT_SUCCESS"]))
	
	# add all the rules into the stylomatic
	for rule in rules:
		styleomatic.enforce(rule)

	# handle command line arguments
	if len(sys.argv) == 1:
		exit(0)
	for arg in sys.argv[1:]:
		if arg[-2:] != ".c":
			styleomatic.failed = True
			print(arg+" is not a c file. Aborting...") 
		elif not os.path.isfile(arg):
			styleomatic.failed = True
			print(arg+" cannot be found. Aborting...") 
		else:
			# actually trigger the stylomatic to check a file
			styleomatic.check(arg,True)
	if not styleomatic.failed:
		print("Awesome Job! No Errors Found!")




