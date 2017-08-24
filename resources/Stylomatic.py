import Tokeniser
from InputStream import InputStream
from Tokeniser import Token

# Rule defines something the stylomatic
# should enforce
# tokenArray : list of tokens that match
#    - specifying the reverse flag causes a failure on match
#    - specifying the lexs array helps match both token and lexme
# ef : the expected form, i.e what the user should be shown as a example
#      of a correctly formed token sequence
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

# Stylomatic must be given indentWidth
# on start so it knows how to enforce
# works with all spaces or all tabs
# but will error on a mix (with a relevant message)
class Stylomatic():
	def __init__(self,indentWidth):
		self.rules = []
                self.errors = []
		self.indentWidth = indentWidth
		self.indentTriggers = {}
		self.failed = False
		self.filename = None
	def enforce(self,rule):
		self.rules.append(rule)
	def enforceIndent(self,tokenType,change):
		self.indentTriggers[tokenType] = change
	def indentation(self,rawTokens):
		i = 0
		tokens = []
		indentWidth = self.indentWidth
		currIndentType = None
		while i < len(rawTokens)-indentWidth:
			token = rawTokens[i]
			if token.type == "tab":
				if currIndentType == None:
					currIndentType = "tab"
				elif currIndentType != "tab":
					self.raiseIndentFailure(token,"A Mix","Either All Tab Or All Space")
					return None
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
						return None
					tokens.append(Token("indent",token.lexme,token.line,token.char))
					i+=indentWidth-1
				else:
					tokens.append(token)
			i+=1

		for i in range(len(rawTokens)-indentWidth,len(rawTokens)):
			token = rawTokens[i]
			if token.type == "tab":
				if currIndentType == None:
					currIndentType = "tab"
				elif currIndentType != "tab":
					self.raiseIndentFailure(token,"A Mix","Either All Tab Or All Space")
					return None
				tokens.append(Token("indent",token.lexme,token.line,token.char))
			else:
				tokens.append(token)

		return tokens
	# check a file for style
	def check(self,filename,debug):
		# get raw tokens
		self.filename = filename
		tokeniser = Tokeniser.Tokeniser(filename)
		rawTokens = []
		while not tokeniser.complete:
			t = tokeniser.getToken()
			rawTokens.append(t)
			if(debug):
				t.show()
		# convert indentWidth spaces / tabs to indents
		tokens = self.indentation(rawTokens)
		if tokens == None:
			return
		# enforce indenting
		self.enforceIndenting(tokens)
		# enforce rest of the rules
		for rule in self.rules:
			self.enforceRule(rule,tokens)
                        self.errors.sort()

        # Show all the collectied errors
        def showErrors(self):
            self.errors.sort()
            errorMessages = [err for line, err in self.errors]
            for i, error in enumerate(errorMessages):
                if error != errorMessages[i-1]:
                    print error

	def enforceIndenting(self,tokens):
		correctIndent = 0
		currIndent = 0
		expect = False
		for i,t in enumerate(tokens):
			# update the correct indent at this token
			if t.type in self.indentTriggers:
				correctIndent += self.indentTriggers[t.type]
			# check if we reset the current indent
			if(t.type == "newLine" and correctIndent > 0):
				expect = True
				currIndent = 0
				continue
			# if we are expecting a indent
			# make sure we got exactly the expected
			# indentation
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
			if rule.tokenArray[curr] == "at":
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
		error = self.filename+": Rule Failed @ line "+str(t.line)+": Expected "+rule.expectedForm
                self.errors.append((t.line, error))
	def raiseIndentFailure(self,t,curr,correct):
		self.failed = True
		errMsg = ""
		if t.lexme == " ":
			errMsg += "Rule Failed @ line %d: "%t.line
			errMsg += "Expected %d Indent(s) But Got %d "%(correct,curr)
			errMsg += "(needed %d spaces)"%(correct*self.indentWidth)
		else:
			errMsg += "Rule Failed @ line %d: "%t.line
			errMsg += "Expected %d Indent(s) But Got %d"%(correct,curr)
		error = self.filename+ ": "+errMsg
                self.errors.append((t.line, error))


# helper function
def generateRule(rules,expr,expectedForm,**kargs):
	dummy = Tokeniser.Tokeniser(None)
	reverse = False
	lexs = []
	exprArray = []
	if expr[0:2] == "!!":
		reverse = True
		expr = expr[2:]

	dummy.stream = InputStream("",raw=expr)
	while not dummy.complete:
		t = dummy.getToken()
		if t.type == "doller":
			exprArray.append(None)
		else:
			exprArray.append(t.type)
		if t.type == "identifier":
			lexs.append(t.lexme)
		else:
			lexs.append(None)
	rules.append(Rule(exprArray,expectedForm,reverse=reverse,lexs=lexs))





