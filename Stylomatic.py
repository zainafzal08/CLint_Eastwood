import Tokeniser
from Tokeniser import Token
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
	def enforce(self,rule):
		self.rules.append(rule)
	def enforceIndent(self,tokenType,change):
		self.indentTriggers[tokenType] = change
	def check(self,filename,debug):
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
					self.raiseIndentFailure(token,"A Mix Of Spaces And Tabs","Either All Tab Or All Space")
				tokens.append(Token("indent",token.lexme,token.line,token.char))
			else:
				if currIndentType == None:
					currIndentType = "space"
				elif currIndentType != "space":
					self.raiseIndentFailure(token,"A Mix Of Spaces And Tabs","Either All Tab Or All Space")
				indnt = True
				for j in range(i,i+indentWidth):
					indnt = indnt and (rawTokens[j].type == "space")
				if indnt:
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
					if(i+1 < len(tokens) and tokens[i].type == "indent"):
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
		print("Rule Failed @ line "+str(t.line)+", char "+str(t.char)+": Expected "+rule.expectedForm)
	def raiseIndentFailure(self,t,curr,correct):
		print("Rule Failed @ line "+str(t.line)+", char "+str(t.char)+": Expected "+str(correct)+" Indent(s) But Got "+str(curr))

if __name__ == "__main__":
	# indet width is 4
	styleomatic = Stylomatic(4)
	# what should indent/unindent
	styleomatic.enforceIndent("openBrace",1)
	styleomatic.enforceIndent("closeBrace",-1)
	# Rules
	rules = []
	rules.append(Rule(["if","space","openBracket"],"if<space>("))
	rules.append(Rule(["else","space","openBrace"],"else<space>{"))
	rules.append(Rule(["while","space","openBracket"],"while<space>("))
	rules.append(Rule(["for","space","openBracket"],"for<space>("))
	rules.append(Rule(["openBracket","space"],"No Space After A Open Bracket",reverse=True))
	rules.append(Rule(["space","closeBracket"],"No Space Before A Close Bracket",reverse=True))
	rules.append(Rule(["space","semicolon"],"No Space Before A Semicolon",reverse=True))
	rules.append(Rule(["identifier",None,"return","space","identifier"],"return EXIT_SUCCESS;",lexs=["main",None,None,None,"EXIT_SUCCESS"]))
	for rule in rules:
		styleomatic.enforce(rule)
	# input fule, False means don't print out debug output
	styleomatic.check("test_basic.c",False)




