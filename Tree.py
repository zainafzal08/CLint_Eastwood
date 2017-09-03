from Lexer import Token

class Node():
	def __init__(self,t):
		self.token = t
		self.children = []

class Tree():
	def __init__(self):
		root = Node("TREE_ROOT")
		self.curr = root
		self.children = []
		self.children.append(root)

	def addTerminal(self,t):
		self.curr.children.append(Node(t))

	def addTrans(self,trans):
		newTrans = Node(trans)
		self.curr.children.append(newTrans)
		self.curr = newTrans
