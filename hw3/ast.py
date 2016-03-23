class DecafClass:
	
	def __init__(self, name, superName, declarations):
		self.name = name
		self.superName = superName
		self.declarations = declarations
		self.fieldTable = []
		self.constructorTable = []
		self.methodTable = []
		# here we actually interpret each declaration and build our
		# symbol tables
		print declarations
		# update the class with the declarations list and subsequently
		# update each of the symbol tables produced for each declaration
		# with the class name
		for record in declarations:
			if isinstance(record, FieldRecord):
				record.containingClass = name
				self.fieldTable.append(record)
			elif isinstance(record, ConstructorRecord):			
				record.containingClass = name
				self.constructorTable.append(record)
				# here we can build the constructor record's variable table
				# we reset the id counter since id's are unique only within
				# the context of each individual variable table
				Variable.variableCounter = 0
				record.variableTable = []
				for param in record.parameters:
					newVar = Variable(param.name, param.type, "formal")
					record.variableTable.append(newVar)
				for stmt in record.statements:
					if isinstance(stmt, VariableDeclaration):
						for name in stmt.names:
							newVar = Variable(name, stmt.type, "local")
							record.variableTable.append(newVar)
							
												
			elif isinstance(record, MethodRecord):			
				record.containingClass = name
				self.methodTable.append(record)
		
	
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

class FieldRecord:

	fieldCounter = 0

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
		s+= self.type.whichType
		print s
		
class ConstructorRecord:

	constructorCounter = 0
	
	def __init__(self, mod, name, parameters, block):
		self.visibility = mod.visibility
		self.applicability = mod.applicability
		self.name = name
		self.parameters = parameters
		# TODO remove this line...
		if not isinstance(block, list):
			self.statements = []
		else:
			self.statements = block
		self.id = ConstructorRecord.constructorCounter
		ConstructorRecord.constructorCounter+=1
		
	def printConstructor(self):
		s = "CONSTRUCTOR: "
		s+= str(self.id)+", "
		s+= self.visibility
		print s
		s = "Constructor parameters: "
		for param in self.parameters:
			s += param.toString()
		print s
		print "Variable Table: "
		for var in self.variableTable:
			print var.toString()	# each variable declaration
									# has its own line
		print "Constructor Body:"
		for stmt in self.statements:
			if not isinstance(stmt, str):
				print stmt.toString()
			else:
				print stmt
		print s
	

class MethodRecord:

	methodCounter = 0

	def __init__(self, mod, returnType, name, parameters, block):
		self.visibility = mod.visibility
		self.applicability = mod.applicability
		self.returnType = returnType
		self.name = name
		self.parameters = parameters
		self.statements = block
		self.id = MethodRecord.methodCounter
		MethodRecord.methodCounter+=1
		
	def printMethod(self):
		print "temp" # TODO
		# s = "CONSTRUCTOR: "
		# s+= str(self.id)+", "
		# s+= self.visibility
		# print s
		# s = "Constructor parameters: "
		# for param in self.parameters:
			# s += param.toString()
		# print s
		# print "Variable Table: "
		# for var in self.variableTable:
			# print var.toString()	# each variable declaration
									# # has its own line
		# print "Constructor Body:"
		# for stmt in self.statements:
			# if not isinstance(stmt, str):
				# print stmt.toString()
			# else:
				# print stmt
		# print s

# useful struct to help pass applicability & visibility information
# in the attribute grammar
class ModStruct:

	def __init__(self, visibility, applicability):
		self.visibility = visibility
		self.applicability = applicability
		
# structs to help pass variable declaration information
class VariableDeclaration:

	def __init__(self, type, names):
		self.type = type
		self.names = names

# variable record
class Variable:

	variableCounter = 0
	
	def __init__(self, name, type, localOrFormal):
		self.type = type
		self.name = name
		self.localOrFormal = localOrFormal
		self.id = variableCounter
		variableCounter+=1
		
	def toString():	
		s = "VARIABLE: "
		s += self.id+", "
		s += self.name+", "
		s += self.localOrFormal+", "
		s += self.type.whichType
		return s

# For CSE 304, this record is a bit redundant since each type could be easily
# expressed as a string (since we don't have arrays!) but for the sake of
# consistency the class is included anyway
class TypeRecord:

	__init__(self, type):
		self.whichType = type
		
# struct intended to represent a single parameter	
class Parameter:

	def __init__(self, type, name):
		self.type = type
		self.name = name
		
	def toString():
		return self.type.whichType+", "+self.name

# a class per statement type
class IfElseStatement:
	
	def __init__(self, cond, thenStmt, elseStmt, startLine, endLine):
		self.cond = cond
		self.thenStmt = thenStmt		
		self.elseStmt = elseStmt
		self.startLine = startLine
		self.endLine = endLine
		
class IfStatement:
	
	def __init__(self, expr, stmt, startLine, endLine):
		self.expr = expr
		self.stmt = stmt
		self.startLine = startLine
		self.endLine = endLine
		
class WhileStatement:
	
	def __init__(self, expr, stmt, startLine, endLine):
		self.expr = expr
		self.stmt = stmt
		self.startLine = startLine
		self.endLine = endLine
		
class ForStatement:

	def __init__(self, init, loopCond, update, body, startLine, endLine):
		self.init = init
		self.loopCond = loopCond
		self.update = update 
		self.body = body
		self.startLine = startLine
		self.endLine = endLine
		
class ReturnStatement:
	
	def __init__(self, ret, startLine, endLine):
		self.ret = ret
		self.startLine = startLine
		self.endLine = endLine

class ExpressionStatement:

	def __init__(self, expr, startLine, endLine):
		self.expr = expr
		self.startLine = startLine
		self.endLine = endLine
		
class BlockStatement:

	def __init__(self, stmts, startLine, endLine):
		self.stmts = stmts
		self.startLine = startLine
		self.endLine = endLine
		
class ContinueStatement:

	def __init__(self, startLine, endLine):
		self.represents = "continue"
		self.startLine = startLine
		self.endLine = endLine
		
class BreakStatement:

	def __init__(self, startLine, endLine):
		self.represents = "break"
		self.startLine = startLine
		self.endLine = endLine
		
class SkipStatement:

	def __init__(self, startLine, endLine):
		self.represents = "empty"
		self.startLine = startLine
		self.endLine = endLine

# a class per expression type
class ConstantIntegerExpression:

	def __init__(self, info, startLine, endLine):
		self.info = info
		self.startLine = startLine
		self.endLine = endLine
		
class ConstantFloatExpression:

	def __init__(self, info, startLine, endLine):
		self.info = info
		self.startLine = startLine
		self.endLine = endLine
		
class ConstantStringExpression:

	def __init__(self, info, startLine, endLine):
		self.info = info
		self.startLine = startLine
		self.endLine = endLine
		
class ConstantNullExpression:

	def __init__(self, startLine, endLine):
		self.info = "null"
		self.startLine = startLine
		self.endLine = endLine
		
class ConstantTrueExpression:

	def __init__(self, startLine, endLine):
		self.info = "true"
		self.startLine = startLine
		self.endLine = endLine
		
class ConstantFalseExpression:

	def __init__(self, startLine, endLine):
		self.info = "false"
		self.startLine = startLine
		self.endLine = endLine
		
class VariableExpression:

	def __init__(self, id, startLine, endLine):
		self.id = id
		self.startLine = startLine
		self.endLine = endLine
		
class UnaryExpression:

	def __init__(self, operator, operand, startLine, endLine):
		self.operator = operator
		self.operand = operand
		self.startLine = startLine
		self.endLine = endLine
		
class BinaryExpression:

	def __init__(self, operator, operand1, operand2, startLine, endLine):
		self.operator = operator
		self.operand1 = operand1
		self.operand2 = operand2
		self.startLine = startLine
		self.endLine = endLine
		
class AssignExpression:

	def __init__(self, leftHandSide, rightHandSide, startLine, endLine):
		self.leftHandSide = leftHandSide
		self.rightHandSide = rightHandSide
		self.startLine = startLine
		self.endLine = endLine
		
class AutoExpression:

	def __init__(self, operand, incOrDec, postOrPre, startLine, endLine):
		self.operand = operand
		self.incOrDec = incOrDec
		self.postOrPre = postOrPre
		self.startLine = startLine
		self.endLine = endLine
		
class FieldAccessExpression:

	def __init__(self, base, name, startLine, endLine):
		self.base = base
		self.name = name
		self.startLine = startLine
		self.endLine = endLine
	
class MethodCallExpression:

	def __init__(self, base, name, args, startLine, endLine):
		self.base = base
		self.name = name
		self.args = args
		self.startLine = startLine
		self.endLine = endLine
	
class NewObjectExpression:

	def __init__(self, base, constructorArgs, startLine, endLine):
		self.base = base
		self.constructorArgs = constructorArgs
		self.startLine = startLine
		self.endLine = endLine
		
class ThisExpression:

	def __init__(self, startLine, endLine):
		self.represents = "this"
		self.startLine = startLine
		self.endLine = endLine
		
class SuperExpression:

	def __init__(self, startLine, endLine):
		self.represents = "super"
		self.startLine = startLine
		self.endLine = endLine
		
class ClassReferenceExpression:

	def __init__(self, name, startLine, endLine):
		self.name = name
		self.startLine = startLine
		self.endLine = endLine
		
# CSE 304 doesn't consider array expressions
#class ArrayAccessExpression:

# CSE 304 doesn't consider array expressions
#class NewArrayExpression: