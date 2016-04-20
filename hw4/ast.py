class DecafClass:
	
	classes = {}
	
	def __init__(self, name, superName, declarations):
		self.name = name
		self.superName = superName
		self.declarations = declarations
		self.fieldTable = []
		self.constructorTable = []
		self.methodTable = []
		# here we actually interpret each declaration and build our
		# symbol tables
		# update the class with the declarations list and subsequently
		# update each of the symbol tables produced for each declaration
		# with the class name
		# must also reset the class counters for methods, fields, and constructors
		ConstructorRecord.constructorCounter = 1
		FieldRecord.fieldCounter = 1
		MethodRecord.methodCounter = 1
		for record in declarations:
			if isinstance(record, FieldRecord):
				record.containingClass = name
				self.fieldTable.append(record)
			elif isinstance(record, ConstructorRecord):			
				record.containingClass = name
				self.constructorTable.append(record)
				# The body statement of the constructor has already generated
				# a variable table for itself, we need only add the constructor
				# parameters to that table
				Variable.variableCounter = len(record.block.variableTable)+1
				for param in record.parameters:
					newVar = Variable(param.name, param.type, "formal")
					if param.name in record.block.variableTable:	
						print "Error, conflicting formal and local variable names."
						print "Formal name on Line "+param.startLine+"."
						print "Local name on Line "+record.block.variableTable[param.name].startLine+"."
					record.block.variableTable[param.name] = newVar
					
				# only after the constructor formal parameters are added to
				# the outermost code blocks' variable table can we properly
				# resolve the local variable names
				for stmt in record.block.stmts:			
					determineVariableExprIDStmt(stmt, record.block)
					
			elif isinstance(record, MethodRecord):			
				record.containingClass = name
				self.methodTable.append(record)				
				# The body statement of the method has already generated
				# a variable table for itself, we need only add the constructor
				# parameters to that table
				Variable.variableCounter = len(record.block.variableTable)+1
				for param in record.parameters:
					newVar = Variable(param.name, param.type, "formal")
					if param.name in record.block.variableTable:						
						print "Error, conflicting formal and local variable names."
						print "Formal name on Line "+param.startLine+"."
						print "Local name on Line "+record.block.variableTable[param.name].startLine+"."
					record.block.variableTable[param.name] = newVar
					
				# only after the method formal parameters are added to
				# the outermost code blocks' variable table can we properly
				# resolve the local variable names
				for stmt in record.block.stmts:			
					determineVariableExprIDStmt(stmt, record.block)
		
		# before completing class construction, we append the class
		# to the class-lookup dictionary
		DecafClass.classes[name] = self
	
	def printClass(self):
		# print fields test code
		print "----------------------------------------------------------"
		print "Class Name: "+self.name
		print "Superclass Name: "+self.superName
		print "Fields: "		
		for f in self.fieldTable:
			f.printField()
		print "Constructors: "
		for c in self.constructorTable:
			c.printConstructor()
		print "Methods: "
		for m in self.methodTable:
			m.printMethod()
			
	def typeCheck(self):
		# type checking will require a recursive pass through each
		# statement and expression in the AST
		# The class is type correct iff each constructor and method are
		# type correct
		for c in self.constructorTable:
			c.typeCheck()
			
		for m in self.methodTable:
			
		

class FieldRecord:

	fieldCounter = 1

	# we update the record with it's containing class
	# during the parse
	def __init__(self, name, type, visibility, applicability):
		self.name = name
		self.id = FieldRecord.fieldCounter
		self.visibility = visibility
		self.applicability = applicability
		self.type = type
		FieldRecord.fieldCounter+=1
		
	def printField(self):
		s = "FIELD: "
		s+= str(self.id)+", "
		s+= self.name+", "
		s+= self.containingClass+", "
		s+= self.visibility+", "
		s+= self.applicability+", "
		s+= self.type.toString()
		print s
		
class ConstructorRecord:

	constructorCounter = 1
	
	def __init__(self, mod, name, parameters, block):
		self.visibility = mod.visibility
		self.applicability = mod.applicability
		self.name = name
		self.parameters = parameters
		self.block = block
		self.id = ConstructorRecord.constructorCounter
		ConstructorRecord.constructorCounter+=1
		
	def printConstructor(self):
		s = "CONSTRUCTOR: "
		s+= str(self.id)+", "
		s+= self.visibility
		print s
		s = "Constructor parameters: "
		temp = []
		for key in self.block.variableTable.keys():
			var = self.block.variableTable[key]
			if (var.localOrFormal == "formal"):
				temp.append(var.id)
		if (len(temp)>0):
			for i in range(0, len(temp)-1):
				s += str(temp[i])+", "
			s += str(temp[len(temp)-1])			
		print s
		print "Variable Table: "
		for key in self.block.variableTable.keys():
			print self.block.variableTable[key].toString()
			# each variable declaration
			# has its own line
		print "Constructor Body:"
		print self.block.toString()
		
	def typeCheck(self):
		ret = True
		for stmt in self.block:
			if not stmt.typeCheck(self):
				ret = False
		return ret

class MethodRecord:

	methodCounter = 1

	def __init__(self, mod, returnType, name, parameters, block):
		self.visibility = mod.visibility
		self.applicability = mod.applicability
		self.returnType = returnType
		self.name = name
		self.parameters = parameters
		self.block = block
		self.id = MethodRecord.methodCounter
		MethodRecord.methodCounter+=1
		
	def printMethod(self):
		s = "METHOD: "
		s+= str(self.id)+", "
		s+= self.name+", "
		s+= self.containingClass+", "
		s+= self.visibility+", "
		s+= self.applicability+", "		
		s+= self.returnType.toString()
		print s
		s = "Method parameters: "
		temp = []
		for key in self.block.variableTable.keys():
			var = self.block.variableTable[key]
			if (var.localOrFormal == "formal"):
				temp.append(var.id)
		if (len(temp)>0):
			for i in range(0, len(temp)-1):
				s += str(temp[i])+", "
			s += str(temp[len(temp)-1])			
		print s
		print "Variable Table: "		
		for key in self.block.variableTable.keys():
			print self.block.variableTable[key].toString()
			# each variable declaration
			# has its own line
		print "Method Body:"
		print self.block.toString()
		
	def typeCheck(self):
		ret = True
		for stmt in self.block:
			if not stmt.typeCheck(self):
				ret = False
				
		return ret

# useful class to help pass applicability & visibility information
# in the attribute grammar
class ModStruct:

	def __init__(self, visibility, applicability):
		self.visibility = visibility
		self.applicability = applicability
		
# class to help pass variable declaration information
class VariableDeclaration:

	def __init__(self, type, names):
		self.type = type
		self.names = names
	
	def toString(self):
		s = self.type.toString()+", "
		for i in range(0, len(self.names)-1):
			s += self.names[i]+", "
		s += self.names[len(self.names)-1]
		return s
			

# class to help pass parameter information
class Parameter:

	def __init__(self, type, name, startLine, endLine):
		self.type = type
		self.name = name
		self.startLine = startLine		
		self.endLine = endLine
		
# variable record
class Variable:

	variableCounter = 1
	
	def __init__(self, name, type, localOrFormal):
		self.type = type
		self.name = name
		self.localOrFormal = localOrFormal
		self.id = Variable.variableCounter
		Variable.variableCounter+=1
		
	def toString(self):	
		s = "VARIABLE: "
		s += str(self.id)+", "
		s += self.name+", "
		s += self.localOrFormal+", "
		s += self.type.whichType
		return s

# For CSE 304, this record is a bit redundant since each type could be easily
# expressed as a string (since we don't have arrays!) but for the sake of
# consistency the class is included anyway
class TypeRecord:

	def __init__(self, type):
		self.whichType = type
		
	# TODO still working out how class literal will be handled....
	
	def toString(self):
		# if the type isn't built-in then the output reflects this
		if(self.whichType == "INT" or
		   self.whichType == "BOOLEAN" or 
		   self.whichType == "FLOAT" or
		   self.whichType == "VOID" or
		   self.whichType == "STRING"):
			return self.whichType
		else:
			return "user("+self.whichType+")"
			
	def isSubType(self, expr):
		# if either type is a built-in type then
		# this method is reduced
		if(self.whichType == "INT" or
		   self.whichType == "BOOLEAN" or 
		   self.whichType == "FLOAT" or
		   self.whichType == "VOID" or
		   self.whichType == "STRING"):
			return self.whichType == expr.type.whichType
		else:
			# in the case that we're not dealing with
			# built-in types we need to search up the
			# subclass structure of the 'self' class
			# until the type of 'expr' is found
			x = self.whichType
			while(x != expr.type.whichType)
				x = classes[x].superName
				if(x is None):
					return False
			return True
			
	
# a class per statement type
class IfElseStatement:
	
	def __init__(self, cond, thenStmt, elseStmt, startLine, endLine):
		self.cond = cond
		self.thenStmt = thenStmt		
		self.elseStmt = elseStmt
		self.startLine = startLine
		self.endLine = endLine
		
	def toString(self):
		s = "IfElse( "+self.cond.toString()
		s += ", "+self.thenStmt.toString()
		s += ", "+self.elseStmt.toString()
		s += " )"
		return s
		
	def typeCheck(self, declaration):					
		return (cond.type.whichType == "BOOLEAN"
							and thenStmt.determineCorrectness(declaration)
							and elseStmt.determineCorrectness(declaration))
		
class IfStatement:
	
	def __init__(self, expr, stmt, startLine, endLine):
		self.expr = expr
		self.stmt = stmt
		self.startLine = startLine
		self.endLine = endLine
		
	def toString(self):
		s = "If( "+self.expr.toString()
		s += ", "+self.stmt.toString()
		s += " )"
		return s
		
	def determineCorrectness(self, declaration):
		if (self.typeChecked):
			return self.isTypeCorrect
		else:
			self.typeChecked = True
			self.isTypeCorrect = (expr.type == "BOOLEAN"
								and stmt.determineCorrectness(declaration))					
			return self.isTypeCorrect
		
class WhileStatement:
	
	def __init__(self, expr, stmt, startLine, endLine):
		self.expr = expr
		self.stmt = stmt
		self.startLine = startLine
		self.endLine = endLine
		
	def toString(self):
		s = "While( "+self.expr.toString()
		s += ", "+self.stmt.toString()
		s += " )"
		return s
		
	def determineCorrectness(self, declaration):
		if (self.typeChecked):
			return self.isTypeCorrect
		else:
			self.typeChecked = True
			self.isTypeCorrect = (expr.type == "BOOLEAN"
								and stmt.determineCorrectness(declaration))					
			return self.isTypeCorrect		
		
class ForStatement:

	def __init__(self, init, loopCond, update, body, startLine, endLine):
		self.init = init
		self.loopCond = loopCond
		self.update = update 
		self.body = body
		self.startLine = startLine
		self.endLine = endLine
		
	def toString(self):
		s = "For( "+self.init.toString()
		s += ", "+self.loopCond.toString()
		s += ", "+self.update.toString()
		s += ", "+self.body.toString()
		s += " )"
		return s
		
	def determineCorrectness(self, declaration):
		if (self.typeChecked):
			return self.isTypeCorrect
		else:
			self.typeChecked = True
			self.isTypeCorrect = (loopCond.type == "BOOLEAN"
								and thenStmt.determineCorrectness(declaration)
								and elseStmt.determineCorrectness(declaration))					
			return self.isTypeCorrect
		
class ReturnStatement:
	
	def __init__(self, ret, startLine, endLine):
		self.ret = ret
		self.startLine = startLine
		self.endLine = endLine
		
	def toString(self):
		s = "Return( "+self.ret.toString()
		s += " )"
		return s
		
	# this is a tricky thing
	# TODO fix this later
	def determineCorrectness(self, declaration):
		return True

class ExpressionStatement:

	def __init__(self, expr, startLine, endLine):
		self.expr = expr
		self.startLine = startLine
		self.endLine = endLine
			
	def toString(self):
		s = "Expr( "+self.expr.toString()
		s += " )"
		return s		

# recursive functions used to ensure that every statement & expression
# has a reference to it's containing block
def setContainingBlockStmt(stmt, block):
	if not (stmt is None):
		stmt.containingBlock = block
		if isinstance(stmt, IfElseStatement):
			setContainingBlockExpr(stmt.cond, block)
			setContainingBlockStmt(stmt.thenStmt, block)
			setContainingBlockStmt(stmt.elseStmt, block)
		elif isinstance(stmt, IfStatement):
			setContainingBlockExpr(stmt.expr, block)
			setContainingBlockStmt(stmt.stmt, block)
		elif isinstance(stmt, WhileStatement):
			setContainingBlockExpr(stmt.expr, block)
			setContainingBlockStmt(stmt.stmt, block)
		elif isinstance(stmt, ForStatement):
			setContainingBlockExpr(stmt.init, block)
			setContainingBlockExpr(stmt.loopCond, block)
			setContainingBlockExpr(stmt.update, block)
			setContainingBlockStmt(stmt.body, block)
		elif isinstance(stmt, ExpressionStatement):
			setContainingBlockExpr(stmt.expr, block)
		elif isinstance(stmt, ReturnStatement):
			setContainingBlockExpr(stmt.ret, block)
		
def setContainingBlockExpr(expr, block):
	if not (expr is None):
		expr.containingBlock = block
		if isinstance(expr, UnaryExpression):
			setContainingBlockExpr(expr.operand, block)
		elif isinstance(expr, BinaryExpression):
			setContainingBlockExpr(expr.operand1, block)
			setContainingBlockExpr(expr.operand2, block)		
		elif isinstance(expr, AssignExpression):
			setContainingBlockExpr(expr.leftHandSide, block)
			setContainingBlockExpr(expr.rightHandSide, block)
		elif isinstance(expr, AutoExpression):
			setContainingBlockExpr(expr.operand, block)
		elif isinstance(expr, FieldAccessExpression):
			setContainingBlockExpr(expr.base, block)
		elif isinstance(expr, MethodCallExpression):				
			setContainingBlockExpr(expr.base, block)
		elif isinstance(expr, NewObjectExpression):
			for x in expr.args:
				setContainingBlockExpr(x, block)

# recursive functions used to ensure that each variable expression
# has it's ID determined directly after the symbol table for its containing
# block is generated
def determineVariableExprIDStmt(stmt, block):
	if not (stmt is None):
		if isinstance(stmt, IfElseStatement):
			determineVariableExprIDExpr(stmt.cond, block)
			determineVariableExprIDStmt(stmt.thenStmt, block)
			determineVariableExprIDStmt(stmt.elseStmt, block)
		elif isinstance(stmt, IfStatement):
			determineVariableExprIDExpr(stmt.expr, block)
			determineVariableExprIDStmt(stmt.stmt, block)
		elif isinstance(stmt, WhileStatement):
			determineVariableExprIDExpr(stmt.expr, block)
			determineVariableExprIDStmt(stmt.stmt, block)
		elif isinstance(stmt, ForStatement):
			determineVariableExprIDExpr(stmt.init, block)
			determineVariableExprIDExpr(stmt.loopCond, block)
			determineVariableExprIDExpr(stmt.update, block)
			determineVariableExprIDStmt(stmt.body, block)
		elif isinstance(stmt, ExpressionStatement):
			determineVariableExprIDExpr(stmt.expr, block)
		elif isinstance(stmt, ReturnStatement):
			determineVariableExprIDExpr(stmt.ret, block)
		elif isinstance(stmt, BlockStatement):
			for x in stmt.stmts:
				determineVariableExprIDStmt(x, block)
		
def determineVariableExprIDExpr(expr, block):
	if not (expr is None):
		if isinstance(expr, UnaryExpression):
			determineVariableExprIDExpr(expr.operand, block)
		elif isinstance(expr, BinaryExpression):
			determineVariableExprIDExpr(expr.operand1, block)
			determineVariableExprIDExpr(expr.operand2, block)		
		elif isinstance(expr, AssignExpression):
			determineVariableExprIDExpr(expr.leftHandSide, block)
			determineVariableExprIDExpr(expr.rightHandSide, block)
		elif isinstance(expr, AutoExpression):
			determineVariableExprIDExpr(expr.operand, block)
		elif isinstance(expr, FieldAccessExpression):
			determineVariableExprIDExpr(expr.base, block)
		elif isinstance(expr, VariableExpression):
			# this is the only expression that we're searching the AST for
			# and therefore this is the only branch for which we take any kind
			# of action
			expr.determineID()
		elif isinstance(expr, MethodCallExpression):				
			determineVariableExprIDExpr(expr.base, block)
		elif isinstance(expr, NewObjectExpression):
			for x in expr.args:
				determineVariableExprIDExpr(x, block)				
				
			
class BlockStatement:

	def __init__(self, stmts, startLine, endLine):
		self.stmts = stmts
		self.startLine = startLine
		self.endLine = endLine
		self.containingBlock = None
		# if every statement and expression maintains a reference to it's
		# containing block, then it's straightforward to determine the id
		# of a given variable expression. This condition is ensured recursively.
		# We can also setup the block variable table here
		variableTable = {}
		Variable.variableCounter = 1
		for stmt in stmts:
			setContainingBlockStmt(stmt, self)
			if isinstance(stmt, VariableDeclarationStatement):
				decl = stmt.varDecl
				for name in decl.names:
					newVar = Variable(name, decl.type, "local")
					if name in variableTable:
						# In this case we already have a variable with
						# this name in the block! Compiler error.
						print "Error - Variable name already defined"
					variableTable[name] = newVar 
		self.variableTable = variableTable
				
				
		# type correctness is done post-synthesis of each declaration
		# and is done only once
		self.isTypeCorrect = False
		self.typeChecked = False
				
	def toString(self):
		s = "Block([ \n"
		if (isinstance(self.stmts, list) and len(self.stmts)>0):
			for i in range(0, len(self.stmts)-1):
				# variable declaration statements are special in the
				# sense that they are NOT printed, so we skip them here
				if not isinstance(self.stmts[i], VariableDeclarationStatement):
					s += " "+self.stmts[i].toString()+"\n ,"
					
			if not isinstance(self.stmts[len(self.stmts)-1], VariableDeclarationStatement):
				s += " "+self.stmts[len(self.stmts)-1].toString()+" \n"
		s += "])"
		return s
		
	def determineCorrectness(self, declaration):
		if (self.typeChecked):
			return self.isTypeCorrect
		else:
			self.typeChecked = True
			# we assume it is type correct until we find a statement
			# that is NOT type correct
			self.isTypeCorrect = True
			for s in self.stmts:
				if(not s.determineCorrectness(declaration)):
					self.isTypeCorrect = False
					
			return self.isTypeCorrect
		
class ContinueStatement:

	def __init__(self, startLine, endLine):
		self.represents = "continue"
		self.startLine = startLine
		self.endLine = endLine
			
	def toString(self):
		s = "Continue( "
		s += " )"
		return s
		
	def determineCorrectness(self, declaration):
		return True
		
class BreakStatement:

	def __init__(self, startLine, endLine):
		self.represents = "break"
		self.startLine = startLine
		self.endLine = endLine
		
	def toString(self):
		s = "Break( "
		s += " )"
		return s
		
	def determineCorrectness(self, declaration):
		return True
		
class SkipStatement:

	def __init__(self, startLine, endLine):
		self.represents = "empty"
		self.startLine = startLine
		self.endLine = endLine
				
	def toString(self):
		s = "Skip( "
		s += " )"
		return s
		
	def determineCorrectness(self, declaration):
		return True
		
class VariableDeclarationStatement:
	
	# wraps a varDecl in a statement class
	def __init__(self, varDecl, startLine, endLine):
		self.varDecl = varDecl
		self.startLine = startLine		
		self.endLine = endLine
		
	def toString(self):
		s = "VariableDeclaration( "
		s += self.varDecl.toString()
		s += " )"
		return s 
		
	def determineCorrectness(self, declaration):
		return True
		# TODO not sure how this one works....

# a class per expression type
class ConstantIntegerExpression:

	def __init__(self, info, startLine, endLine):
		self.info = info
		self.startLine = startLine
		self.endLine = endLine
		self.type = TypeRecord("INT")
		
	def toString(self):
		s = "ConstantInteger( "
		s += str(self.info)
		s += " )"
		return s
		
	def getType(self):
		return self.type
		
class ConstantFloatExpression:

	def __init__(self, info, startLine, endLine):
		self.info = info
		self.startLine = startLine
		self.endLine = endLine
		self.type = TypeRecord("FLOAT")
		
	def toString(self):
		s = "ConstantFloat( "
		s += str(self.info)
		s += " )"
		return s
	
	def getType(self):
		return self.type
		
class ConstantStringExpression:

	def __init__(self, info, startLine, endLine):
		self.info = info
		self.startLine = startLine
		self.endLine = endLine
		self.type = TypeRecord("STRING")
		
	def toString(self):
		s = "ConstantString( "
		s += self.info
		s += " )"
		return s
		
	def getType(self):
		return self.type
		
class ConstantNullExpression:

	def __init__(self, startLine, endLine):
		self.info = "null"
		self.startLine = startLine
		self.endLine = endLine
		self.type = TypeRecord("NULL")
		
	def toString(self):
		s = "ConstantNull( "
		s += self.info
		s += " )"
		return s
		
	def getType(self):
		return self.type
		
class ConstantTrueExpression:

	def __init__(self, startLine, endLine):
		self.info = "true"
		self.startLine = startLine
		self.endLine = endLine
		self.type = TypeRecord("BOOLEAN")
		
	def toString(self):
		s = "ConstantTrue( "
		s += self.info
		s += " )"
		return s
		
	def getType(self):
		return self.type
		
class ConstantFalseExpression:

	def __init__(self, startLine, endLine):
		self.info = "false"
		self.startLine = startLine
		self.endLine = endLine
		self.type = TypeRecord("BOOLEAN")
		
	def toString(self):
		s = "False"
		return s
		
	def getType(self):
		return self.type
		
class VariableExpression:

	def __init__(self, name, startLine, endLine):
		self.name = name
		self.startLine = startLine
		self.endLine = endLine
		self.id = None
	
	def toString(self):
		s = "Variable( "
		if self.id is None:
			self.determineID()
		s += str(self.id)
		s += " )"
		return s
		
	def determineID(self):
		whichBlock = self.containingBlock
		while not (self.name in whichBlock.variableTable):
			if whichBlock.containingBlock is None:
				print "ERROR - Symbol "+self.name+" not found. Line "+str(self.startLine)+"."
				self.id = -1
				return				
			whichBlock = whichBlock.containingBlock
		self.id = (whichBlock.variableTable[self.name]).id
		
		# we keep a reference to the type of the variable that this expression
		# references
		self.type = whichBlock.variableTable[self.name].type
		
	def getType(self):
		return self.type
		
class UnaryExpression:

	def __init__(self, operator, operand, startLine, endLine):
		self.operator = operator
		self.operand = operand
		self.startLine = startLine
		self.endLine = endLine	
		self.type = None
		
	def toString(self):
		s = "UnaryExpr( "
		s += self.operator + ", "
		s += self.operand.toString()
		s += " )"
		return s
		
	def getType(self):		
		# type is defined by the used operator
		# if the operand doesn't match the operator then
		# the expression isn't type correct and the type is "ERROR"
		if (self.type is None):
			if(operator == "!"):
				if(operand.getType() == "BOOLEAN"):
					self.type = TypeRecord("BOOLEAN")
				else:
					# operand-operator type mismatch
					self.type = TypeRecord("ERROR")
			elif(operator == "-" or operator == "+"):
				if(operand.getType() == "INT"):
					self.type = TypeRecord("INT")
				elif(operand.getType() == "FLOAT"):
					self.type = TypeRecord("FLOAT")
				else:
					# operand-operator type mismatch
					self.type = TypeRecord("ERROR")
					
		return self.type
		
class BinaryExpression:

	def __init__(self, operator, operand1, operand2, startLine, endLine):
		self.operator = operator
		self.operand1 = operand1
		self.operand2 = operand2
		self.startLine = startLine
		self.endLine = endLine
		self.type = None
		
	def toString(self):
		s = "BinaryExpr( "
		s += self.operator + ", "
		s += self.operand1.toString() + ", "
		s += self.operand2.toString() + ", "
		s += " )"
		return s
		
	def getType(self):
		# Type checking must be performed post AST construction. In particular,
		# we cannot know the subclass structure until we have processed all of
		# the classes!
		if (self.type is None):
			# type is defined by the used operator
			# if the operand doesn't match the operator then
			# the expression isn't type correct and the type is "ERROR"
			if (operator == "+" or
				operator == "-" or
				operator == "*" or
				operator == "/"):
				if(operand1.getType() == "INT" and
				   operand2.getType() == "INT"):
					self.type = TypeRecord("INT")
				elif(operand1.getType() == "FLOAT" and
					 operand2.getType() == "FLOAT"):
					self.type = TypeRecord("FLOAT")
				else:
					self.type = TypeRecord("ERROR")
			elif(operator == "&&" or
				 operator == "||"):
				if(operand1.getType() == "BOOLEAN" and
				   operand2.getType() == "BOOLEAN"):
					self.type = TypeRecord("BOOLEAN")
				else:
					self.type = TypeRecord("ERROR")
			elif(operator == "<" or
				 operator == "<=" or
				 operator == ">" or
				 operator == ">="):
				if(operand1.getType() == "INT" and
				   operand2.getType() == "INT"):
					self.type = TypeRecord("BOOLEAN")
				elif(operand1.getType() == "FLOAT" and
					 operand2.getType() == "FLOAT"):
					self.type = TypeRecord("BOOLEAN"))
				else:
					self.type = TypeRecord("ERROR")
			elif(operator == "==" or
				 operator == "!="):
				if(operand1.getType().isSubType(operand2) or
				   operand2.getType().isSubType(operand1)):
					self.type = TypeRecord("BOOLEAN")
				else:
					self.type = TypeRecord("ERROR")
					
		return self.type
		
class AssignExpression:

	def __init__(self, leftHandSide, rightHandSide, startLine, endLine):
		self.leftHandSide = leftHandSide
		self.rightHandSide = rightHandSide
		self.startLine = startLine
		self.endLine = endLine
		self.type = None
				
	def toString(self):
		s = "Assign( "
		s += self.leftHandSide.toString() + ", "
		s += self.rightHandSide.toString()
		s += " )"
		return s
		
	def getType(self):
		if (self.type is None):
			rhs = self.rightHandSide.getType()
			lhs = self.leftHandSide.getType() 
			if (rhs.isSubType(self.leftHandSide)
				and rhs.whichType != "ERROR"
				and lhs.whichType != "ERROR"):
				self.type = rhs
			else:
				self.type = TypeRecord("ERROR")
		return self.type
		
class AutoExpression:

	def __init__(self, operand, incOrDec, postOrPre, startLine, endLine):
		self.operand = operand
		self.incOrDec = incOrDec
		self.postOrPre = postOrPre
		self.startLine = startLine
		self.endLine = endLine
				
	def toString(self):
		s = "AutoExpr( "
		s += self.operand.toString() + ", "
		s += self.incOrDec + ", "
		s += self.postOrPre
		s += " )"
		return s
		
	def getType(self):
		if(self.type is None):
			if(operand.getType().whichType == "INT"):
				self.type = TypeRecord("INT")
			elif(operand.getType().whichType == "FLOAT"):
				self.type = TypeRecord("FLOAT")
			else:
				self.type = TypeRecord("ERROR")
		return self.type
		
class FieldAccessExpression:

	def __init__(self, base, name, startLine, endLine):
		self.base = base
		self.name = name
		self.startLine = startLine
		self.endLine = endLine
			
	def toString(self):
		s = "FieldAccess( "
		if not (self.base is None):
			if isinstance(self.base, str):
				s += self.base+", "
			else:
				s += self.base.toString() + ", "
		s += self.name
		s += " )"
		return s
	
class MethodCallExpression:

	def __init__(self, base, name, args, startLine, endLine):
		self.base = base
		self.name = name
		self.args = args
		self.startLine = startLine
		self.endLine = endLine
			
	def toString(self):
		s = "MethodCall( "
		
		if not (self.base is None):
			if isinstance(self.base, str):
				s += self.base+", "
			else:
				s += self.base.toString() + ", "
		
		s += self.name + ", "
		s += "Arguments([ "
		if( isinstance(self.args, list) and len(self.args)>0):
			s += "\n"
			for i in range(0, len(self.args)-1):
				s += self.args[i].toString()+", \n"
			s += self.args[len(self.args-1)].toString()+" \n"			
		s += "])"		
		s += " )"
		return s
	
class NewObjectExpression:

	def __init__(self, base, args, startLine, endLine):
		self.base = base
		self.args = args
		self.startLine = startLine
		self.endLine = endLine
		
	def toString(self):
		s = "NewObject( "		
		if not (self.base is None):
			# TODO this may be an error....
			if isinstance(self.base, str):
				s += self.base+", "
			else:
				s += self.base.toString() + ", "
		s += "Arguments([ "
		if( isinstance(self.args, list) and len(self.args)>0):
			s += "\n"
			for i in range(0, len(self.args)-1):
				s += self.args[i].toString()+", \n"
			s += self.args[len(self.args)-1].toString()+" \n"			
		s += "])"		
		s += " )"
		return s
		
class ThisExpression:

	def __init__(self, startLine, endLine):
		self.represents = "this"
		self.startLine = startLine
		self.endLine = endLine
			
	def toString(self):
		s = "This"
		return s
		
class SuperExpression:

	def __init__(self, startLine, endLine):
		self.represents = "super"
		self.startLine = startLine
		self.endLine = endLine
			
	def toString(self):
		s = "Super"
		return s
		
class ClassReferenceExpression:

	def __init__(self, name, startLine, endLine):
		self.name = name
		self.startLine = startLine
		self.endLine = endLine
					
	def toString(self):
		s = "ClassReference( "
		s += self.name
		s += " )"
		return s
		
# CSE 304 doesn't consider array expressions
#class ArrayAccessExpression:

# CSE 304 doesn't consider array expressions
#class NewArrayExpression: