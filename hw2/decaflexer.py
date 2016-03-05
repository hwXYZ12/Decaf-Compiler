# module: decaflexer.py
# This module only contains the token specification of the decaf lexer

# Reserved words use a single rule with a special lookup function
reserved = {
	'boolean' : 'BOOLEAN',
	'break' : 'BREAK',
	'continue' : 'CONTINUE',
	'class' : 'CLASS',
	'do' : 'DO',
	'else' : 'ELSE',
	'extends' : 'EXTENDS',
	'false' : 'FALSE',
	'float' : 'FLOAT',
	'for' : 'FOR',
	'if' : 'IF',
	'int' : 'INT',
	'new' : 'NEW',
	'null' : 'NULL',
	'private' : 'PRIVATE',
	'public' : 'PUBLIC',
	'return' : 'RETURN',
	'static' : 'STATIC',
	'super' : 'SUPER',
	'this' : 'THIS',
	'true' : 'TRUE',
	'void' : 'VOID',
	'while' : 'WHILE'
	}

# List of token names
tokens = [
	'COMMENT',
	'MULTILINE_COMMENT',
	'INT_CONST',
	'FLOAT_CONST',
	'STRING_CONST',
	'BOOL_AND',				  
	'BOOL_OR',
	'EQUAL',
	'NOT_EQUAL',
	'LESS_THAN_OR_EQUAL',
	'GREATER_THAN_OR_EQUAL',
	'PLUS_PLUS',
	'MINUS_MINUS',
	'ID'
	] + list(reserved.values())
	
	
# All whitespace is automatically ignored by the lexer and is also not a part
# of the decaf language, so we can leave that as default behavior

# Comments, on the other hand, are specified as C-style multi-line /* */
# and are specified in function form since they should be the first thing to be
# ignored
def t_MULTILINE_COMMENT(t):
	r'/\*([^\*]|\n)*\*/'
	pass
		
def t_COMMENT(t):
	r'//.*'
	pass

# explicitly define whitespace to be ignored in the tokenization process
# (note that newlines are handled later in order to keep track of line numbers!)
t_ignore = ' \t'
	
# Regular expression rules for simple tokens
t_INT_CONST = r'[0-9]+'
t_FLOAT_CONST = r'[0-9]+\.[0-9]+' # note that we don't care about leading zeros! we are also CSE 304 and don't care about
								  # the second type of float
t_STRING_CONST = r'"([^"]|\n)*"'  # CSE 304 only checks for the next " symbol to terminate the string constant
								  
# since longer regular expressions are added first, we can be confident
# that unary and binary operators that have multiple character representations will be recognized
# for what they are intended to be as opposed to two tokens of single character literals	
# we also don't need to worry that any of these will be matched in identifiers since they are not
# supposed to be in any identifiers anyway!
t_BOOL_AND = r'&&'						  
t_BOOL_OR = r'\|\|'
t_EQUAL = r'=='
t_NOT_EQUAL = r'!='
t_LESS_THAN_OR_EQUAL = r'<='
t_GREATER_THAN_OR_EQUAL = r'>='
t_PLUS_PLUS = r'\+\+'
t_MINUS_MINUS = r'--'
								  
# After checking for comments and constants, we check for identifiers
# Note, if the identifier is a reserved word, then the previously defined lookup
# function will be useful in realizing it
def t_ID(t):
	r'[a-zA-Z][a-zA-Z_0-9]*'
	t.type = reserved.get(t.value,'ID') # check for reserved words
	return t
				
# After defining most of the other rules, we define our set of literals
# ALTHOUGH WE ARE CSE 304 AND DO NOT SUPPORT ANY OF THE ARRAY VALUED FIELDS AND VARIABLES!!!
# This makes things a bit more interesting when it comes to the parser, but for now we will include
# the [] characters in our definition of literals
literals = "()[]{}\+-\*/!;,=><."		
								
# Define a rule so we can track line numbers, taken directly from the manual
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule, also taken from the manual
# For the purpose of our assignment, this error message will cause the comp
def t_error(t):
    print("Illegal character '%s' on line %d" % (t.value[0], t.lineno) )