import ply.lex as lex
import ply.yacc as yacc
import basicGrammarLexer
import sys
from basicGrammarLexer import tokens
from basicGrammarParser import *

print "Please enter the filename of a basic grammar that you'd like generate LR(1) tables for. Terminate input with Ctrl-Z on Windows and Ctrl-D on Unix: "

input = sys.stdin.readline()

# remove the new line character from the filename
length = len(input)
input = input[:length - 1]

while True:
	# main program will continue to try to open a file until it is opened
	try:
		file = open(input)
		productionList = file.read()
		break;
	except:
		print "ERROR - File could not be opened / read. Please try again. Please enter the filename of a decaf program to check for syntax errors: "
		input = sys.stdin.readline()
		# remove the new line character from the filename
		length = len(input)
		input = input[:length - 1]

# generate the lexer first
lexer = lex.lex(module = basicGrammarLexer)
lexer.input(productionList)

for tok in lexer:
	print tok
	
# generate the parser using the grammar specified in decafparser.py
parser = yacc.yacc()
	
try:
	parser.parse(productionList)
	print "If there are no syntax errors listed above, then the scan & parse was successful and the input is a grammatically valid list of productions."
except:
	print "A scanning / parsing error has occurred. Program will now terminate."
	sys.exit(0)
	
class Production:

	def __init__(self, leftHandSide, rightHandSide):
		self.leftHandSide = leftHandSide
		self.rightHandSide = rightHandSide
		
lexer.input(productionList)
productions = []
for tok in lexer:
	if(tok.type == "LHS"):
		production = Production(tok.value[:len(tok.value)-2], [])
		productions.append(production)
	else:
		if(tok.type == "TERMINAL"):
			production.rightHandSide.append((tok.value,"TERMINAL"))
		elif(tok.type == "NONTERMINAL"):
			production.rightHandSide.append((tok.value,"NONTERMINAL"))
		
# ensure that if a production has no right hand side then it is considered
# a production that has at least the empty string as the right hand side
for index in range(len(productions)):
	if(len(productions[index].rightHandSide) == 0):
		productions[index].rightHandSide.add(("", "EMPTY_STRING"))
		
class LR1Item:

	# dot is intended to represent the index of an imagined "dot" that signifies
	# left context of an LR1Item. For example, for a production A->BCD, we might
	# have a dot with position 0. This implies that the dot is here: A->*BCD.
	# Similarly, dot = 1 corresponds to A->B*CD, dot = 2 corresponds to A->BC*D
	# An easy way to think about it is that 'dot' represents how many symbols
	# in right hand side of the production are to the left of the dot
	def __init__(self, production, dot):
		self.production = production
		self.dot = dot
		
# Before we begin our algorithm, we need to determine the goal symbol. The goal
# symbol should be the only nonterminal in our list of productions which does
# NOT appear in the right hand side of any production. This symbol should be
# unique.
nonterminals = set()
terminals = set()
rightHandNonTerminals = set()
for production in productions:
	nonterminals.add(production.leftHandSide)
	for pair in production.rightHandSide :
		if(pair[1] == "TERMINAL"):
			terminals.add(pair[0])
		elif(pair[1] == "NONTERMINAL"):
			nonterminals.add(pair[0])
			rightHandNonTerminals.add(pair[0])

candidates = set()
for symbol in nonterminals :
	if(symbol not in rightHandNonTerminals):
		candidates.add(symbol)
		
if(len(candidates) == 0):
	# no goal symbol found, return an error and quit
	print "No goal symbol found in the grammar! Program will now terminate."
	sys.exit(0)
elif(len(candidates) > 1):
	# too many goal symbols found, return an error and quit
	print "Too many goal symbols found in the grammar! Program will now terminate."
	sys.exit(0)

goalSymbol = candidates.pop()

# initialize the list of lr1item sets and the first set
CC = []
CC.append(set())

# build the initial state of the first set
for production in productions:
	if(production.rightHandSide == goalSymbol):
		CC[0].add(LR1Item(production, 0))
		
# define the 'First' dictionary that will take a nonterminal and return
# the set of possible terminals that a sentence derived from the given
# nonterminal can begin with
First = {}
for t in terminals:
	First[t] = set([t])
First[""] = set([""])
for nt in nonterminals:
	First[nt] = set()
	
stillChanging = True
while(stillChanging):
	stillChanging = False
	for p in productions:
		k = len(p.rightHandSide) - 1
		temp = First[(p.rightHandSide[0])[0]] - First[""]
		i = 0
		while("" in First[(p.rightHandSide[i])[0]] and i <= k-1):
			temp = temp | (First[(p.rightHandSide[i+1])[0]] -  First[""])
			i = i + 1
		if (i==k and "" in First[(p.rightHandSide[k])[0]]):
			temp = temp | First[""]
		for x in temp:
			if x not in First[p.leftHandSide]:
				stillChanging = True
		First[p.leftHandSide] = First[p.leftHandSide] | temp
		
def first(symbols):
	ret = set()
	for index in range(len(symbols)):
		ret = ret | First(x)
		if "" not in First(x)
			break
	
	hasEmptyString = True
	for s in symbols:
		if "" not in First(x):
			hasEmptyString = False
	
	if(hasEmptyString):
		ret.add("")
	else:
		ret = ret - First[""]
	
	return ret
		
# closure algorithm that takes a core set of LR1Items and adds to the set
# any LRItems that are implied by the LR1Items in the core set

print First
	
	