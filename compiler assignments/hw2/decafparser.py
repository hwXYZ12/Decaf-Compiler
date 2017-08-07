import ply.yacc as yacc
from decaflexer import tokens

def p_program(p):
	r'''program : class_decl program
			    | empty'''
			   

def p_class_decl(p):
	r'''class_decl : CLASS ID '(' EXTENDS ID ')' placeholder1
				  | CLASS ID placeholder1
	placeholder1 : '{' class_body_decl placeholder2 '}'
	placeholder2 : class_body_decl placeholder2
				 | empty
	class_body_decl : field_decl
					| method_decl
					| constructor_decl'''
						
def p_field_decl(p):
	r'''field_decl : modifier var_decl ';'
	modifier : placeholder3 placeholder4
	placeholder3 : PUBLIC
				 | PRIVATE
				 | empty
	placeholder4 : STATIC
				 | empty
	var_decl : type variables
	type : INT
		 | FLOAT
		 | BOOLEAN
		 | ID
	variables : variable placeholder5
	placeholder5 : ',' variable placeholder5
				 | empty
	variable : ID'''
		 
def p_method_decl(p):
	r'''method_decl : modifier type ID '(' placeholder7 ')' block
					| modifier VOID ID '(' placeholder7 ')' block
	constructor_decl : modifier ID '(' placeholder7 ')' block
	placeholder7 : formals
				 | empty
	formals : formal_param placeholder8
	placeholder8 : ',' formal_param placeholder8
				 | empty
	formal_param : type variable'''
		
# if-then-else "dangling" ifs ambiguity resolved using something I Googled
def p_block(p):
	r'''block : '{' placeholder9 '}'
	placeholder9 : stmt placeholder9
			 | empty
	stmt : openStmt
		 | closedStmt
	openStmt : IF '(' expr ')' stmt
			 | IF '(' expr ')' closedStmt ELSE openStmt
		 | WHILE '(' expr ')' openStmt
		 | FOR '(' placeholder11 ';' placeholder12 ';' placeholder11 ')' openStmt
	closedStmt : RETURN placeholder12 ';'
		   | stmt_expr ';'
		   | BREAK ';'
		   | CONTINUE ';'
		   | var_decl
		   | ';' 
		   | block
		   | IF '(' expr ')' closedStmt ELSE closedStmt
		   | WHILE '(' expr ')' closedStmt
		   | FOR '(' placeholder11 ';' placeholder12 ';' placeholder11 ')' closedStmt
	placeholder11 : stmt_expr
			  | empty
	placeholder12 : expr
			  | empty'''
				  
def p_primary(p):
	r'''literal : INT_CONST
			   | FLOAT_CONST
			   | STRING_CONST
			   | NULL
			   | TRUE
			   | FALSE
	primary : literal
			| THIS
			| SUPER
			| '(' expr ')'
			| NEW ID '(' placeholder14 ')'
			| lhs
			| method_invocation
	placeholder14 : arguments
				  | empty
	arguments : expr placeholder15
	placeholder15 : ',' expr placeholder15
				  | empty
	lhs : field_access
	field_access : primary '.' ID
				 | ID
	method_invocation : field_access '(' placeholder14 ')' '''
	
def p_expr(p):
	r'''expr : assign
			 | p1
	assign : lhs '=' expr
		   | lhs PLUS_PLUS
		   | PLUS_PLUS lhs
		   | lhs MINUS_MINUS
		   | MINUS_MINUS lhs
	p1 : p1 BOOL_OR p2
	   | p2
	p2 : p2 BOOL_AND p3
	   | p3
	p3 : p3 EQUAL p4
	   | p3 NOT_EQUAL p4
	   | p4
	p4 : p4 '<' p5
	   | p4 '>' p5
	   | p4 LESS_THAN_OR_EQUAL p5
	   | p4 GREATER_THAN_OR_EQUAL p5
	   | p5
	p5 : p5 '+' p6
	   | p5 '-' p6
	   | p6
	p6 : p6 '*' p7
	   | p6 '/' p7
	   | p7
	p7 : '!' p7
	   | '+' p7
	   | '-' p7
	   | primary'''
	   
def p_stmt_expr(p):
	r'''stmt_expr : assign
				  | method_invocation'''
				
def p_empty(p):
	'empty :'
	pass
				
def p_error(p):
    if p:
		print("Syntax error '%s' on line %d" % (p.value, p.lineno))
		print(p)
    else:
        print("Syntax error at EOF")
	
