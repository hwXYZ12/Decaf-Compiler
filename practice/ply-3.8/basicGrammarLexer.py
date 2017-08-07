# module: basicGrammarLexer.py
# This module contains the token specification for a basic grammar lexer

# List of token names
tokens = [
	'TERMINAL',
	'NONTERMINAL',
	'LHS'
	]
	
# White space is not completely ignored...

# Comments are not allowed... these grammars are extremely simple

# regular expressions
def t_LHS(t):
	r'[^\s][^\s]+\s:'
	return t
	
def t_NONTERMINAL(t):
	r'[^\s][^\s]+'
	return t

def t_TERMINAL(t):
	r'[^\s]'		
	return t

# ignore whitespace
t_ignore = " \t\n\r\f\v"
	
								
# Define a rule so we can track line numbers, taken directly from the manual
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule, also taken from the manual
# This error message will print which line the lexing error occurred and
# the token itself
def t_error(t):
    print("Illegal character '%s' on line %d" % (t.value[0], t.lineno) )