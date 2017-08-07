import ply.yacc as yacc
from basicGrammarLexer import tokens

def p_grammar(p):
	'''ProductionList : Production ProductionList
					   | empty
		Production : LHS RightHand 
		RightHand : NONTERMINAL RightHand 
				  | TERMINAL RightHand 
				  | empty '''
				
def p_empty(p):
	'empty :'
	pass
				
def p_error(p):
    if p:
		print("Syntax error '%s' on line %d" % (p.value, p.lineno))
		print(p)
    else:
        print("Syntax error at EOF")