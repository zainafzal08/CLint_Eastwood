import Tokeniser
from Stylomatic import Stylomatic,generateRule
from InputStream import InputStream
from Tokeniser import Token
import sys
import os

# indent width is enforced at 4
styleomatic = Stylomatic(4)

# what should trigger a indent/unindent
styleomatic.enforceIndent("openBrace",1)
styleomatic.enforceIndent("closeBrace",-1)

# Rules
# -------------------------------------------------------------
# arg 1: the list you want to append the rule object to
# arg 2: the expression you which to match
#        if it starts with !! the cheker enforces no match
#        the $ symbol acts as a wild card (i.e .* in regex)
#        the @ symbol acts as a singlular wild card (i.e . in regex)
# arg 3: the expected form of the line that is printed out with
#        the error message
rules = []
generateRule(rules,"if ($) {","if (<expr>) {")
generateRule(rules,"else {","else {")
generateRule(rules,"while ($) {","while (<expr>) {")
generateRule(rules,"for ($) {","for (<expr>) {")
generateRule(rules,"{\n","A new line after {")
generateRule(rules,"}@\n","A new line after }")
generateRule(rules,"!!( ","No Space After A Open Bracket")
generateRule(rules,"!! )","No Space Before A Open Bracket")
generateRule(rules,"!! ;","No Space Before A Semicolon")
generateRule(rules,"main(int argc, char *argv[]) {","A Main Function Structured as 'main(int argc, char *argv[]) {'")
generateRule(rules,"main$return EXIT_SUCCESS","single return statement 'return EXIT_SUCCESS;'")

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
		# the False just turns off debugging
		styleomatic.check(arg,False)
if not styleomatic.failed:
	print("Awesome Job! No Errors Found!")