import ply.lex as lex
import ply.yacc as yacc
import decaflexer
import sys
from decaflexer import tokens
from decafparser import *

print "Please enter the filename of a decaf program to check for syntax errors. Terminate input with Ctrl-Z on Windows and Ctrl-D on Unix: "

input = sys.stdin.readline()
# remove the new line character from the filename
length = len(input)
input = input[:length - 1]

while True:
	# main program will continue to try to open a file until it is opened
	try:
		file = open(input)
		program = file.read()
		break;
	except:
		print "ERROR - File could not be opened / read. Please try again. Please enter the filename of a decaf program to check for syntax errors: "
		input = sys.stdin.readline()
		# remove the new line character from the filename
		length = len(input)
		input = input[:length - 1]

# generate the lexer first
lexer = lex.lex(module = decaflexer)
lexer.input(program)
	
# generate the parser using the grammar specified in decafparser.py
parser = yacc.yacc()
	
try:
	parser.parse(program)
	print "If there are no syntax errors listed above, then the scan & parse was successful and the input is a grammatically valid decaf program."
except:
	print "A scanning / parsing error has occurred. Program will now terminate."