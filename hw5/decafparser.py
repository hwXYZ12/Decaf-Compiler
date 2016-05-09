import ply.yacc as yacc
import decaflexer
from decaflexer import tokens
#from decaflexer import errorflag
from decaflexer import lex
import ast
from ast import *

import sys
import logging
precedence = (
    ('right', 'ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LEQ', 'GEQ', 'LT', 'GT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
    ('right', 'ELSE'),
    ('right', 'RPAREN'),
)


def init():
    decaflexer.errorflag = False

# keep track of decaf classes using a list
classes = []

# the AST is going to be initialized with two classes already made:
# In: Consider this as a class with no fields, no constructors, but with the following two methods:
# 		scan_int: a public static method that takes no parameters, with a return type of int.
# 		scan_float: a public static method that takes no parameters, with a return type of float.
# Out: Consider this as a class with no fields, no constructors, but with the following four methods:
# 		print: a public static method that takes one formal parameter (for convenience, call it i) of type int, and returns nothing.
# 		print: a public static method that takes one formal parameter (for convenience, call it f) of type float, and returns nothing.
# 		print: a public static method that takes one formal parameter (for convenience, call it b) of type boolean, and returns nothing.
# 		print: a public static method that takes one formal parameter (for convenience, call it s) of type string, and returns nothing.
methodList = [MethodRecord(ModStruct("public","static"), TypeRecord("INT"), "scan_int",  [], BlockStatement([], 0, 0)),
			  MethodRecord(ModStruct("public","static"), TypeRecord("FLOAT"), "scan_float",  [], BlockStatement([], 0, 0))]
classes.append(DecafClass("In", "", methodList))
methodList = [MethodRecord(ModStruct("public","static"), TypeRecord("VOID"), "print",  [Parameter(TypeRecord("INT"), "i", 0, 0)], BlockStatement([], 0, 0)),
			  MethodRecord(ModStruct("public","static"), TypeRecord("VOID"), "print",  [Parameter(TypeRecord("FLOAT"), "f", 0, 0)], BlockStatement([], 0, 0)),
			  MethodRecord(ModStruct("public","static"), TypeRecord("VOID"), "print",  [Parameter(TypeRecord("BOOLEAN"), "b", 0, 0)], BlockStatement([], 0, 0)),
			  MethodRecord(ModStruct("public","static"), TypeRecord("VOID"), "print",  [Parameter(TypeRecord("STRING"), "s", 0, 0)], BlockStatement([], 0, 0))]
classes.append(DecafClass("Out", "", methodList))


### DECAF Grammar

# Top-level
def p_pgm(p):
    'pgm : class_decl_list'
    pass

def p_class_decl_list_nonempty(p):
    'class_decl_list : class_decl class_decl_list'
def p_class_decl_list_empty(p):
    'class_decl_list : '
    pass

def p_class_decl(p):
	'class_decl : CLASS ID extends LBRACE class_body_decl_list RBRACE'
	# create a new DecafClass instance and pass its constructor
	# it's name, it's superclass name, and a set of all its declarations
	classes.append(DecafClass(p[2],p[3], p[5]))
	
def p_class_decl_error(p):
	'class_decl : CLASS ID extends LBRACE error RBRACE'
    # error in class declaration; skip to next class decl.
	classes.append(DecafClass(p[2],p[3], p[5]))
	pass

def p_extends_id(p):
	'extends : EXTENDS ID '
	p[0] = p[2]
	pass
def p_extends_empty(p):
	' extends : '
	p[0] = ""
	pass

def p_class_body_decl_list_plus(p):
	'class_body_decl_list : class_body_decl_list class_body_decl'
	# creates and passes up a list of declarations
	# we only have 3 possibilities for declarations
	# - constructor
	# - method
	# - field declaration(s)
	x = p[1]
	decl = p[2]	
	# we ensure that "class_body_decl_list" represents
	# a list of declarations that has at least one element
	if not isinstance(x, list):
		prevList = [x]
	else:
		prevList = x
		
	if isinstance(decl, list):
		if len(decl)>0 and isinstance(decl[0], FieldRecord):
			# we know we're dealing with field declaration(s)
			for f in decl:			
				prevList.append(f)
				p[0] = prevList
	else:
		# the other two declarations are not lists
		prevList.append(decl)
		p[0] = prevList
	pass
def p_class_body_decl_list_single(p):
	'class_body_decl_list : class_body_decl'
	decl = p[1]
	if(isinstance(decl, list)):
		p[0] = decl
	else:
		p[0] = [decl]
	pass
	
def p_class_body_decl_field(p):
	'class_body_decl : field_decl'
	# a list of field records are created and passed upwards
	p[0] = p[1]
	pass
def p_class_body_decl_method(p):
	'class_body_decl : method_decl'
	# a single method record is created and passed upwards
	p[0] = p[1]
	pass
def p_class_body_decl_constructor(p):
	'class_body_decl : constructor_decl'
	# a single constructor record is created and passed upwards
	p[0] = p[1]
	pass


# Field/Method/Constructor Declarations

def p_field_decl(p):
	'field_decl : mod var_decl'
	# the 'var_decl' symbol could reduce to multiple field
	# declarations with the same visibility and applicability
	# thus we're going to work with a synthesized list of
	# declarations
	mod = p[1]
	varDecl = p[2]
	varList = varDecl.names
	fieldRecords = []
	for x in varList:
		newRecord = FieldRecord(x, varDecl.type, mod.visibility, mod.applicability)
		fieldRecords.append(newRecord)
	p[0] = fieldRecords
	pass

def p_method_decl_void(p):
	'method_decl : mod VOID ID LPAREN param_list_opt RPAREN block'
	p[0] = MethodRecord(p[1], TypeRecord("VOID"), p[3], p[5], p[7])
	pass
def p_method_decl_nonvoid(p):
	'method_decl : mod type ID LPAREN param_list_opt RPAREN block'
	p[0] = MethodRecord(p[1], p[2], p[3], p[5], p[7])
	pass

def p_constructor_decl(p):
	'constructor_decl : mod ID LPAREN param_list_opt RPAREN block'
	p[0] = ConstructorRecord(p[1], p[2], p[4], p[6])
	pass


def p_mod(p):
	'mod : visibility_mod applicability_mod'
	# create a ModStruct to pass upwards
	#  ModStruct will contain information about the visibility
	# of the declaration(s) and whether it/they is/are static or not
	p[0] = ModStruct(p[1], p[2])
	pass

def p_visibility_mod_pub(p):
	'visibility_mod : PUBLIC'
	p[0] = "public"
	pass
def p_visibility_mod_priv(p):
	'visibility_mod : PRIVATE'
	p[0] = "private"
	pass
def p_visibility_mod_empty(p):
	'visibility_mod : '
	# if unspecified, defaults to private
	p[0] = "private"
	pass

def p_applicability_mod_static(p):
	'applicability_mod : STATIC'
	p[0] = "static"
	pass
def p_applicability_mod_empty(p):
	'applicability_mod : '
	p[0] = "instance"
	pass

def p_var_decl(p):
	'var_decl : type var_list SEMICOLON'
	# var_decl passes up both the type of the declaration
	# and a list containing the variable IDs
	# if structure ensures that it is indeed a list passed upwards
	p[0] = VariableDeclaration(p[1], p[2])
	pass

# we aren't going to use an enum for types though since
# types can vary depending on user-defined types
def p_type_int(p):
	'type :  INT'
	p[0] = TypeRecord("INT")
	pass
def p_type_bool(p):
	'type :  BOOLEAN'
	p[0] = TypeRecord("BOOLEAN")
	pass
def p_type_float(p):
	'type :  FLOAT'
	p[0] = TypeRecord("FLOAT")
	pass
def p_type_id(p):
	'type :  ID'
	p[0] = TypeRecord(p[1])
	pass

def p_var_list_plus(p):
	'var_list : var_list COMMA var'
	# var_list could be a single variable name or a list
	# of variable names (we know that var will always be a single name)
	x = p[1]
	y = p[3]
	x.append(y)
	p[0] = x
	pass
def p_var_list_single(p):
	'var_list : var'
	p[0] = [p[1]]

def p_var_id(p):
	'var : ID'
	p[0] = p[1]
	pass

# CSE 304 doesn't deal with arrays
#def p_var_array(p):
#    'var : var LBRACKET RBRACKET'
#    pass

def p_param_list_opt(p):
	'param_list_opt : param_list'
	p[0] = p[1]
	pass
def p_param_list_empty(p):
	'param_list_opt : '
	p[0] = []
	pass

def p_param_list(p):
	'param_list : param_list COMMA param'
	# ensure that a list is always returned
	x = p[1]
	y = p[3]
	x.append(y)
	p[0] = x
	pass
def p_param_list_single(p):
	'param_list : param'
	p[0] = [p[1]]
	pass

def p_param(p):
	'param : type var'
	p[0] = Parameter(p[1], p[2], p.lineno(1), p.lineno(2))
	pass

# Statements

def p_block(p):
	'block : LBRACE stmt_list RBRACE'
	stmtList = p[2]
	if( isinstance(stmtList, list) and len(stmtList)>0):
		firstStmt = stmtList[0]
		lastStmt = stmtList[len(stmtList)-1]
		p[0] = BlockStatement(stmtList, firstStmt.startLine, lastStmt.endLine)
	else:
		p[0] = BlockStatement(stmtList, p.lineno(1), p.lineno(3))
	pass
def p_block_error(p):
	'block : LBRACE stmt_list error RBRACE'
    # error within a block; skip to enclosing block	
	p[0] = p[2]
	pass

def p_stmt_list_empty(p):
	'stmt_list : '
	p[0] = [SkipStatement(-1, -1)] # skip statements won't have line numbers
	pass
def p_stmt_list(p):
	'stmt_list : stmt_list stmt'
	stmts = p[1]
	if(len(stmts) == 1 and isinstance(stmts[0], SkipStatement)):
		# replace the skip statement
		stmts[0] = p[2]
	else:
		stmts.append(p[2])	
	p[0] = stmts
	pass


def p_stmt_if_else(p):
	'stmt : IF LPAREN expr RPAREN stmt ELSE stmt'
	expr = p[3]
	elseStmt = p[7]
	p[0] = IfElseStatement(expr, p[5], elseStmt, expr.startLine, elseStmt.endLine)
	pass
def p_stmt_if(p):
	'stmt : IF LPAREN expr RPAREN stmt'	
	expr = p[3]
	stmt = p[5]
	p[0] = IfStatement(expr, stmt, expr.startLine, stmt.endLine)
	pass
def p_stmt_while(p):
	'stmt : WHILE LPAREN expr RPAREN stmt'	
	expr = p[3]
	stmt = p[5]
	p[0] = WhileStatement(expr, stmt, expr.startLine, stmt.endLine)
	pass
def p_stmt_for(p):
	'stmt : FOR LPAREN stmt_expr_opt SEMICOLON expr_opt SEMICOLON stmt_expr_opt RPAREN stmt'
	init = p[3]
	loopCond = p[5]
	updateExpr = p[7]
	body = p[9]
	p[0] = ForStatement(init, loopCond, updateExpr, body, init.startLine, body.endLine)
	pass
def p_stmt_return(p):
	'stmt : RETURN expr_opt SEMICOLON'
	p[0] = ReturnStatement(p[2], p.lineno(1), p.lineno(3))
	pass
def p_stmt_stmt_expr(p):
	'stmt : stmt_expr SEMICOLON'
	expr = p[1]
	p[0] = ExpressionStatement(expr, expr.startLine, expr.endLine)
	pass
def p_stmt_break(p):
	'stmt : BREAK SEMICOLON'
	p[0] = BreakStatement(p.lineno(1), p.lineno(2))
	pass
def p_stmt_continue(p):
	'stmt : CONTINUE SEMICOLON'
	p[0] = ContinueStatement(p.lineno(1), p.lineno(2))
	pass
def p_stmt_block(p):
	'stmt : block'
	p[0] = p[1]
	pass
def p_stmt_var_decl(p):
	'stmt : var_decl'
	# variable decalarations are special, they are NOT printed during
	# the print out!
	p[0] = VariableDeclarationStatement(p[1], p.lineno(1), p.lineno(1))
	pass
def p_stmt_error(p):
	'stmt : error SEMICOLON'
	p[0] = p[1]
	print("Invalid statement near line {}".format(p.lineno(1)))
	decaflexer.errorflag = True

# Expressions
def p_literal_int_const(p):
	'literal : INT_CONST'
	p[0] = ConstantIntegerExpression(int(p[1]), p.lineno(1), p.lineno(1))
	pass
def p_literal_float_const(p):
	'literal : FLOAT_CONST'
	p[0] = ConstantFloatExpression(float(p[1]), p.lineno(1), p.lineno(1))
	pass
def p_literal_string_const(p):
	'literal : STRING_CONST'
	p[0] = ConstantStringExpression(str(p[1]), p.lineno(1), p.lineno(1))
	pass
def p_literal_null(p):
	'literal : NULL'
	p[0] = ConstantNullExpression(p.lineno(1), p.lineno(1))
	pass
def p_literal_true(p):
	'literal : TRUE'
	p[0] = ConstantTrueExpression(p.lineno(1), p.lineno(1))
	pass
def p_literal_false(p):
	'literal : FALSE'
	p[0] = ConstantFalseExpression(p.lineno(1), p.lineno(1))
	pass

def p_primary_literal(p):
	'primary : literal'
	p[0] = p[1]
	pass
def p_primary_this(p):
	'primary : THIS'
	p[0] = ThisExpression(p.lineno(1), p.lineno(1))
	pass
def p_primary_super(p):
	'primary : SUPER'
	p[0] = SuperExpression(p.lineno(1), p.lineno(1))
	pass
def p_primary_paren(p):
	'primary : LPAREN expr RPAREN'
	p[0] = p[2]
	pass
def p_primary_newobj(p):
	'primary : NEW ID LPAREN args_opt RPAREN'
	p[0] = NewObjectExpression(p[2], p[4], p.lineno(1), p.lineno(5))
	pass
def p_primary_lhs(p):
	'primary : lhs'
	p[0] = p[1]
	pass
def p_primary_method_invocation(p):
	'primary : method_invocation'
	p[0] = p[1]
	pass

def p_args_opt_nonempty(p):
	'args_opt : arg_plus'
	p[0] = p[1]
	pass
def p_args_opt_empty(p):
	'args_opt : '
	p[0] = []
	pass

def p_args_plus(p):
	'arg_plus : arg_plus COMMA expr'
	args = p[1]
	p[0] = args.append(p[3][0])
	pass
def p_args_single(p):
	'arg_plus : expr'
	p[0] = [p[1]]
	pass

# CSE 304 doesn't consider arrays, edited to reflect this
def p_lhs(p):
	'lhs : field_access'
	p[0] = p[1]
	pass

def p_field_access_dot(p):
	'field_access : primary DOT ID'
	p[0] = FieldAccessExpression(p[1], p[3], p.lineno(1), p.lineno(3))
	pass
# for CSE 304 the rules are a bit different... we can use a different
# expression object for 'field_access : ID' since method calls are never
# implicit (ie, we can guarantee that this production is a reduction to a
# variable name or else a compiler error has occurred)
def p_field_access_id(p):
	'field_access : ID'
	# since we only pass information upwards, associating this variable expression
	# with it's containing block (and by extension the block's symbol table)
	# must be done retro-actively after the parse has completed
	p[0] = VariableExpression(p[1], p.lineno(1), p.lineno(1))
	pass

# CSE 304 doesn't consider arrays, edited to reflect this 
#def p_array_access(p):
#	'array_access : primary LBRACKET expr RBRACKET'
#	pass

def p_method_invocation(p):
	'method_invocation : field_access LPAREN args_opt RPAREN'
	fieldAccess = p[1]
	p[0] = MethodCallExpression(fieldAccess.base, fieldAccess.name, p[3], p.lineno(1), p.lineno(4))
	pass

# CSE 304 doesn't consider arrays, edited to reflect this
def p_expr_basic(p):
	'''expr : primary
			| assign'''
	p[0] = p[1]
	pass
def p_expr_binop(p):
	'''expr : expr PLUS expr
			| expr MINUS expr
			| expr MULTIPLY expr
			| expr DIVIDE expr
			| expr EQ expr
			| expr NEQ expr
			| expr LT expr
			| expr LEQ expr
			| expr GT expr
			| expr GEQ expr
			| expr AND expr
			| expr OR expr
	'''
	expr1 = p[1]
	expr2 = p[3]
	symbol = p[2]
	p[0] = BinaryExpression(symbol, expr1, expr2, p.lineno(1), p.lineno(3))	
	pass
def p_expr_unop(p):
	'''expr : PLUS expr %prec UMINUS
			| MINUS expr %prec UMINUS
			| NOT expr'''
	expr = p[2]
	p[0] = UnaryExpression(p[1], expr, expr.startLine, expr.endLine)
	pass

def p_assign_equals(p):
	'assign : lhs ASSIGN expr'
	lhs = p[1]
	rhs = p[3]
	p[0] = AssignExpression(lhs, rhs, p.lineno(1), p.lineno(3))
	pass
def p_assign_post_inc(p):
	'assign : lhs INC'
	p[0] = AutoExpression(p[1], "increment", "post", p.lineno(1), p.lineno(2))
	pass
def p_assign_pre_inc(p):
	'assign : INC lhs'
	p[0] = AutoExpression(p[2], "increment", "pre", p.lineno(1), p.lineno(2))
	pass
def p_assign_post_dec(p):
	'assign : lhs DEC'
	p[0] = AutoExpression(p[1], "decrement", "post", p.lineno(1), p.lineno(2))
	pass
def p_assign_pre_dec(p):
	'assign : DEC lhs'
	p[0] = AutoExpression(p[2], "decrement", "pre", p.lineno(1), p.lineno(2))
	pass

# CSE 304 doesn't consider arrays, edited to reflect this
#def p_new_array(p):
#    'new_array : NEW type dim_expr_plus dim_star'
#    pass

# CSE 304 doesn't consider arrays, edited to reflect this
# def p_dim_expr_plus(p):
    # 'dim_expr_plus : dim_expr_plus dim_expr'
    # pass
# def p_dim_expr_single(p):
    # 'dim_expr_plus : dim_expr'
    # pass

# def p_dim_expr(p):
    # 'dim_expr : LBRACKET expr RBRACKET'
    # pass

# def p_dim_star(p):
    # 'dim_star : LBRACKET RBRACKET dim_star'
    # pass
# def p_dim_star_empty(p):
    # 'dim_star : '
    # pass

def p_stmt_expr(p):
	'''stmt_expr : assign
				 | method_invocation'''
	p[0] = p[1]
	pass

def p_stmt_expr_opt(p):
	'stmt_expr_opt : stmt_expr'
	p[0] = p[1]
	pass
def p_stmt_expr_empty(p):
	'stmt_expr_opt : '
	p[0] = None
	pass

def p_expr_opt(p):
	'expr_opt : expr'
	p[0] = p[1]
	pass
def p_expr_empty(p):
	'expr_opt : '
	p[0] = None
	pass


def p_error(p):
    if p is None:
        print ("Unexpected end-of-file")
    else:
        print ("Unexpected token '{0}' near line {1}".format(p.value, p.lineno))
    decaflexer.errorflag = True

parser = yacc.yacc()

def from_file(filename):
	try:
		with open(filename, "rU") as f:
			init()	
			
			# debug code
			# lexer=lex.lex(module=decaflexer)
			# lexer.input(f.read())
			
			# for t in lexer:
				# print t
			
			parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=None)
		return not decaflexer.errorflag
	except IOError as e:
		print "I/O error: %s: %s" % (filename, e.strerror)


if __name__ == "__main__" :
    f = open(sys.argv[1], "r")
    logging.basicConfig(
            level=logging.CRITICAL,
    )
    log = logging.getLogger()
    res = parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=log)

    if parser.errorok :
        print("Parse succeed")
    else:
        print("Parse failed")
