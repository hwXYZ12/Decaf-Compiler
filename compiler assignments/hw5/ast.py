class DecafClass:
	
	classes = {}
	staticOffset = 0
	
	# a static attribute used to help determine the size
	# of the static area heap that will be allocated
	totalStaticFields = 0
		
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
		# we must also reset the class counters for fields
		FieldRecord.fieldCounter = 1
		
		for record in declarations:
			if isinstance(record, FieldRecord):
				record.containingClass = name
				self.fieldTable.append(record)
			elif isinstance(record, ConstructorRecord):			
				record.containingClass = name
				self.constructorTable.append(record)
								
				# each formal parameter recieves it's own argument
				# register for use later when generating AMI
				if (record.applicability == "static"):
					argCount = 0
				else:
					argCount = 1
				
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
													
					# set AMI argument registers
					newVar.currentRegister = "a"+str(argCount)
					argCount += 1
					
				# only after the constructor formal parameters are added to
				# the outermost code blocks' variable table can we properly
				# resolve the local variable names
				for stmt in record.block.stmts:			
					determineVariableExprIDStmt(stmt, record.block)
					
			elif isinstance(record, MethodRecord):			
				record.containingClass = name
				self.methodTable.append(record)	

				# each formal parameter recieves it's own argument
				# register for use later when generating AMI
				if (record.applicability == "static"):
					argCount = 0
				else:
					argCount = 1
				
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
					
					# set AMI argument registers
					newVar.currentRegister = "a"+str(argCount)
					argCount += 1
					
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
			# a second pass to ensure that all constructor variable expressions are
			# resolved including classes and class literals
			for stmt in c.block.stmts:			
				determineVariableExprIDStmt(stmt, c.block)	
			if not (c.typeCheck(self)):
				print "ERROR - A type error in a constructor has occurred."
			
		for m in self.methodTable:
			# a second pass to ensure that all method variable expressions are
			# resolved including classes and class literals
			for stmt in m.block.stmts:			
				determineVariableExprIDStmt(stmt, m.block)			
			if not (m.typeCheck(self)):
				print "ERROR - A type error in a method has occurred."
		
	# convert the class to Abstract Machine Instructions
	# and return the result as a string
	def getAMI(self):
	
		s = ""
		
		# convert each constructor to Abstract Machine Instructions
		# and concatenate the result
		for c in self.constructorTable:	
			s += c.getAMI(self)
			# each constructor doesn't have a return
			# statement for the compiler to automatically
			# append a 'ret' instruction so we must add one
			# here
			s += "\nret"
			s += "\n\n"	# newline characters added for readability
		
		# convert each method to Abstract Machine Instructions
		# and concatenate the result		
		for m in self.methodTable:
			s += m.getAMI(self)
			s += "\n\n"
			
		# count each static field in the class
		for f in self.fieldTable:
			if(f.applicability == "static"):
				DecafClass.totalStaticFields+=1
				
		return s

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
		
		# when a new static field record is added to the
		# AST it is assigned a static offset for later
		# use
		if(applicability == "static"):
			self.staticOffset = DecafClass.staticOffset
			DecafClass.staticOffset += 1
		
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
		self.branchCounter = 0
		self.tempRegCounter = -1
		
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
		
	def typeCheck(self, containingClass):
		ret = True
		for stmt in self.block.stmts:
			if not stmt.typeCheck(containingClass, self):
				print "ERROR - A statement isn't type correct. Lines "+str(stmt.startLine)+" to "+str(stmt.endLine)+"."
				ret = False
		return ret
		
	# convert this constructor into Abstract Machine Instructions
	# and return those instructions as a string
	def getAMI(self, containingClass):
		
		# the first instruction is always a label of the form
		# 'C_%s_%d' where %s is the name of the class and %d
		# is the unique id
		s = self.getAMILabel()+":"
		
		# the block that this method contains is converted
		# to AMI and concatenated with the returned string		
		t = self.block.getAMI(containingClass, self, "NONE", "NONE")
		if (t != ""):
			s += "/n" + t
		
		return s
		
	def getAMILabel(self):
		return "C_"+self.name+"_"+str(self.id)
		

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
		MethodRecord.methodCounter += 1
		self.branchCounter = 0
		self.tempRegCounter = -1
		
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
		temp = self.block.variableTable.keys()
		# force the variables to be printed in order
		# and on separate lines
		for index in range(0, len(temp)):			
			for key in temp:
				if(self.block.variableTable[key].id == (index+1)):				
					print self.block.variableTable[key].toString()
		print "Method Body:"
		print self.block.toString()
			
	def typeCheck(self, containingClass):
		ret = True
		for stmt in self.block.stmts:
			if not stmt.typeCheck(containingClass, self):
				print "ERROR - A statement isn't type correct. Lines "+str(stmt.startLine)+" to "+str(stmt.endLine)+"."
				ret = False
		return ret

	# convert this method into Abstract Machine Instructions
	# and return those instructions as a string
	def getAMI(self, containingClass):
		
		# the first instruction is always a label of the form
		# 'M_%s_%d' where %s is the name of this method and %d
		# is the unique id
		s = self.getAMILabel()+":\n"
		
		# the block that this method contains is converted
		# to AMI and concatenated with the returned string
		s += self.block.getAMI(containingClass, self, "NONE", "NONE")
		
		return s
		
	def getAMILabel(self):
		return "M_"+self.name+"_"+str(self.id)
		
		
		
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
		self.currentRegister = None
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
		
	# whether or not the type record represents a class-literal depends
	# on the context which is not information contained directly within
	# a type record
	
	def toString(self):
		# if the type isn't built-in then the output reflects this
		if(self.isBuiltIn()):
			return self.whichType
		else:
			return "user("+self.whichType+")"
			
	def isSubType(self, typeRecord):
	
		# CSE 304 ignores arrays altogether
	
		# any type is a subtype of itself
		if(self.whichType == typeRecord.whichType):
			return True
		
		# int is a subtype of float
		if(self.whichType == "INT"
			and typeRecord.whichType == "FLOAT"):
			return True			
			
		# null is a subtype of any class
		if(self.whichType == "NULL"
			and not typeRecord.isBuiltIn()):
			return True			
			
		# if either type is a built-in type then
		# this method is reduced
		if self.isBuiltIn():
			return self.whichType == typeRecord.whichType
		else:			
			# in the case that we're not dealing with
			# built-in types we need to search up the
			# subclass structure of the 'self' class
			# until the type of 'typeRecord' is found
			x = self.whichType
			while(x != typeRecord.whichType):
				if not (x in DecafClass.classes):
					return False
				x = DecafClass.classes[x].superName
				if(x is None):
					return False
			return True
	
	def isBuiltIn(self):
		return (self.whichType == "INT" or
		   self.whichType == "BOOLEAN" or 
		   self.whichType == "FLOAT" or
		   self.whichType == "VOID" or
		   self.whichType == "STRING" or
		   self.whichType == "NULL" or
		   self.whichType == "ERROR")
	
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
		
	def typeCheck(self, containingClass, declaration):				
		return (self.cond.getType(containingClass).whichType == "BOOLEAN"
							and self.thenStmt.typeCheck(containingClass, declaration)
							and self.elseStmt.typeCheck(containingClass, declaration))
	
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# An if else branch is implemented using AMI jumps and labels
		# if (condition)
		# <statements>
		# (and skip the following else statements)
		# else
		# (ensure that the if statements are skipped)
		# <statements>
		#
		# becomes...
		# if not (condition) jump to labelx
		# <statements>
		# jump to labely
		# labelx:
		# <statements>
		# labely:
		declaration.branchCounter += 1
		labelx = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
		declaration.branchCounter += 1
		labely = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
		
		# we need both to generate the code that will compute the condition
		# and we also need the register containing the result
		condition = self.cond.getAMI(containingClass, declaration, breakLabel, continueLabel)
		cReg = self.cond.resultReg
		
		# first we evaluate the condition expression
		s = condition + "\n"
		
		# now we add the branching structure described above
		s += "bz "+cReg+", "+labelx+"\n"
		s += self.thenStmt.getAMI(containingClass, declaration, breakLabel, continueLabel) + "\n"
		s += "jmp "+labely+"\n"
		s += labelx+":\n"
		s += self.elseStmt.getAMI(containingClass, declaration, breakLabel, continueLabel) + "\n"
		s += labely+":"
		return s
		
		
		
	
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
		
	def typeCheck(self, containingClass, declaration):					
		return (self.expr.getType(containingClass).whichType == "BOOLEAN"
							and self.stmt.typeCheck(containingClass, declaration))
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# An if branch is the same as an ifelse branch except 
		# there is no 'else' code
		# if (condition)
		# <statements>
		# (and skip the following else statements)
		# else
		# (ensure that the if statements are skipped)
		#
		# becomes...
		# if not (condition) jump to labelx
		# <statements>
		# labelx:
		declaration.branchCounter += 1
		labelx = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
		
		# we need both to generate the code that will compute the condition
		# and we also need the register containing the result
		condition = self.cond.getAMI(containingClass, declaration, breakLabel, continueLabel)
		cReg = self.cond.resultReg
		
		# first we evaluate the condition expression
		s = condition + "\n"
		
		# now we add the branching structure described above
		s += "bz "+cReg+", "+labelx+"\n"
		s += self.stmt.getAMI(containingClass, declaration, breakLabel, continueLabel) + "\n"
		s += labelx+":"
		return s
		
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
		
	def typeCheck(self, containingClass, declaration):					
		return (self.expr.getType(containingClass).whichType == "BOOLEAN"
							and stmt.typeCheck(containingClass, declaration))
	
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# A while loop has this structure...
		# while (condition)
		# <statements>
		# loop back and repeat
		#
		# in pseudo-assembly becomes....
		# startLoop:
		# if not (condition) jump to endLoop
		# <statements>
		# jump to startLoop
		# endLoop:
		
		# generate labels
		declaration.branchCounter += 1
		startLoop = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
		
		declaration.branchCounter += 1
		endLoop = declaration.getAMILabel()+"_"+str(declaration.branchCounter)		
		
		# we need both to generate the code that will compute the condition
		# and we also need the resulting register
		condition = self.cond.getAMI(containingClass, declaration, breakLabel, continueLabel)
		cReg = self.cond.resultReg
		
		# first we evaluate the condition expression
		s = condition + "\n"
		
		# note that we now have a new continue label
		# as well as a break label
		continueLabel = startLoop
		breakLabel = endLoop		
		
		# set the first label
		s = startLoop+":\n"
		
		# now we add the rest of the branching structure described above
		s += "bz "+cReg+", "+endLoop+"\n"
		s += self.stmt.getAMI(containingClass, declaration, breakLabel, continueLabel) + "\n"
		s += "jmp "+startLoop+"\n"
		s += endLoop+":"
		return s							
		
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
		
	def typeCheck(self, containingClass, declaration):
		return (self.loopCond.getType(containingClass).whichType == "BOOLEAN"
				and self.init.getType(containingClass).whichType != "ERROR"
				and self.update.getType(containingClass).whichType != "ERROR"
				and self.body.typeCheck(containingClass, declaration))
				
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# A for loop has the following structure...
		# init
		# for (condition)
		# <statements>
		# loop back, update, and repeat
		#
		# in pseudo-assembly becomes....
		# <init assignment or method invocation>
		# startLoop:
		# if not (condition) jump to endLoop
		# <statements>
		# <update assignment or method invocation>
		# jump to startLoop
		# endLoop:
		
		# generate labels
		declaration.branchCounter += 1
		startLoop = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
		
		declaration.branchCounter += 1
		endLoop = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
		
		# we need both to generate the code that will compute the condition
		# and we also need the resulting register
		condition = self.loopCond.getAMI(containingClass, declaration, breakLabel, continueLabel)
		cReg = self.loopCond.resultReg
		
		# start with the init expression
		s = self.init.getAMI(containingClass, declaration, breakLabel, continueLabel) + "\n"
		
		# note that we now have a new continue label
		# as well as a break label
		continueLabel = startLoop
		breakLabel = endLoop
		
		# set the first label
		s += startLoop+":\n"
		
		# first we evaluate the condition expression
		s += condition + "\n"
		
		# now we add the rest of the branching structure described above
		s += "bz "+cReg+", "+endLoop+"\n"
		s += self.body.getAMI(containingClass, declaration, breakLabel, continueLabel) + "\n"
		s += self.update.getAMI(containingClass, declaration, breakLabel, continueLabel) + "\n"
		s += "jmp "+startLoop+"\n"
		s += endLoop+":"
		return s
		
class ReturnStatement:
	
	def __init__(self, ret, startLine, endLine):
		self.ret = ret
		self.startLine = startLine
		self.endLine = endLine
		
	def toString(self):
		if not (self.ret is None):
			s = "Return( "+self.ret.toString()
			s += " )"
		else:
			s = "Return( )"
		return s
		
	def typeCheck(self, containingClass, declaration):
		if (self.ret is None):
			check = declaration.returnType.whichType == "VOID"
			if not check:
				print "ERROR - Return type mismatch. Line "+str(self.startLine)+"."
			return check
		else:
			check = self.ret.getType(containingClass).isSubType(declaration.returnType)
			if not check:
				print "ERROR - Return type mismatch. Line "+str(self.startLine)+"."
			return check
			
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# Generating the code for the return statement will also generate another
		# register. We move that result to the a0 register and add a 'ret' instruction
		s = self.ret.getAMI(containingClass, declaration, breakLabel, continueLabel)
		if (s != ""):
			s += "\n"
		s += "move a0, "+self.ret.resultReg+"\n"
		s += "ret"
		return s
			

class ExpressionStatement:

	def __init__(self, expr, startLine, endLine):
		self.expr = expr
		self.startLine = startLine
		self.endLine = endLine
			
	def toString(self):
		s = "Expr( "+self.expr.toString()
		s += " )"
		return s		
		
	def typeCheck(self, containingClass, declaration):
		return self.expr.getType(containingClass).whichType != "ERROR"
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		return self.expr.getAMI(containingClass, declaration, breakLabel, continueLabel)


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
			for x in expr.args:
				setContainingBlockExpr(x, block)
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
			for x in expr.args:
				determineVariableExprIDExpr(x, block)
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
		
	def typeCheck(self, containingClass, declaration):
		ret = True
		for s in self.stmts:
			if not (s.typeCheck(containingClass, declaration)):
				ret = False
		return ret
		
	# convert each statement in this block to Abstract Machine Instructions
	# and return the result as a string
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):		
		s = ""
		for stmt in self.stmts:
			temp = stmt.getAMI(containingClass, declaration, breakLabel, continueLabel)	
			if(temp != ""):
				if (s != ""):
					s += "\n"+temp
				else:
					s += temp
		return s
		
class ContinueStatement:

	def __init__(self, startLine, endLine):
		self.represents = "continue"
		self.startLine = startLine
		self.endLine = endLine
			
	def toString(self):
		s = "Continue( "
		s += " )"
		return s
		
	def typeCheck(self, containingClass, declaration):
		return True
	
	# In order to branch properly this portion of code will need some context
	# In particular it will need to know where to jump to! A continue statement
	# only makes sense inside of a loop. We recursively pass break and
	# continue labels from branching statements and use these to properly
	# branch.
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# this method will assume that the break and continue labels
		# were set properly
		return "jump "+continueLabel
		
class BreakStatement:

	def __init__(self, startLine, endLine):
		self.represents = "break"
		self.startLine = startLine
		self.endLine = endLine
		
	def toString(self):
		s = "Break( "
		s += " )"
		return s
		
	def typeCheck(self, containingClass, declaration):
		return True
	
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):		
		# this method will assume that the break and continue labels
		# were set properly
		return "jump "+breakLabel
		
class SkipStatement:

	def __init__(self, startLine, endLine):
		self.represents = "empty"
		self.startLine = startLine
		self.endLine = endLine
				
	def toString(self):
		s = "Skip( "
		s += " )"
		return s
		
	def typeCheck(self, containingClass, declaration):
		return True
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# skip statement represents the lack of an instruction
		return ""
		
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
		
	def typeCheck(self, containingClass, declaration):
		# these statements are more or less always type correct by default
		# their correctness is determined during AST construction (that is,
		# the only error that can arise from declaring variables is either
		# a malformed statement that will be found during lexical analysis
		# or an over-writing of a variable already declared in the same scope
		# that will be found during AST construction)
		return True
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# doesn't do anything directly with regards to AMI except assigns
		# a set of temporary registers to each variable within a block
		whichBlock = self.containingBlock
		for x in whichBlock.variableTable:
			y = whichBlock.variableTable[x]
			if (y.localOrFormal == "local"):
				# get a new register for each local variable	
				if(y.currentRegister is None):
					declaration.tempRegCounter += 1	
					y.currentRegister = "t"+str(declaration.tempRegCounter)					
		return ""

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
		
	def getType(self, containingClass):
		return self.type
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# generate a temporary register and use it to access the constant
		declaration.tempRegCounter += 1
		self.resultReg = "t"+str(declaration.tempRegCounter)
		
		s = "move_immediate_i "+self.resultReg+", "+str(self.info)
		return s
		
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
	
	def getType(self, containingClass):
		return self.type
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# generate a temporary register and use it to access the constant
		declaration.tempRegCounter += 1
		self.resultReg = "t"+str(declaration.tempRegCounter)
		
		s = "move_immediate_f "+self.resultReg+", "+str(self.info)
		return s
		
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
		
	def getType(self, containingClass):
		return self.type
		
	# for hw 5, we aren't considering string constants
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# return the constant as it is
		self.resultReg = "NO RESULT REGISTER"
		return "IGNORE"
		
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
		
	def getType(self, containingClass):
		return self.type
		
	# we're going to use 0 for null values / null pointers
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# generate a temporary register and use it to access the constant
		declaration.tempRegCounter += 1
		self.resultReg = "t"+str(declaration.tempRegCounter)
		
		s = "move_immediate_i "+self.resultReg+", 0"
		return s
		
		
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
		
	def getType(self, containingClass):
		return self.type
		
	# we'll use 1 to represent 'true'
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# generate a temporary register and use it to access the constant
		declaration.tempRegCounter += 1
		self.resultReg = "t"+str(declaration.tempRegCounter)
		
		s = "move_immediate_i "+self.resultReg+", 1"
		return s
		
class ConstantFalseExpression:

	def __init__(self, startLine, endLine):
		self.info = "false"
		self.startLine = startLine
		self.endLine = endLine
		self.type = TypeRecord("BOOLEAN")
		
	def toString(self):
		s = "False"
		return s
		
	def getType(self, containingClass):
		return self.type
		
	# we'll use 0 to represent 'false'
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):		
		# generate a temporary register and use it to access the constant
		declaration.tempRegCounter += 1
		self.resultReg = "t"+str(declaration.tempRegCounter)
		
		s = "move_immediate_i "+self.resultReg+", 0"
		return s
		
class VariableExpression:

	def __init__(self, name, startLine, endLine):
		self.name = name
		self.startLine = startLine
		self.endLine = endLine
		self.id = None
		self.isClassLiteral = False
	
	def toString(self):
		if self.id is None:
			self.determineID()			
		s = ""
		if (self.isClassLiteral):
			s = "ClassLiteral( "
			s += self.name
		else:
			s = "Variable( "
			s += str(self.id)
		s += " )"			
		return s
		
	def determineID(self):
		
		# it is possible that this expression cannot be resolved
		# because it in fact represents a class literal
		# this function will be called a second time once all classes
		# have been synthesized and here that will be corrected
		if(self.id == -1):
			if self.name in DecafClass.classes:
				self.isClassLiteral = True
				self.type = TypeRecord(self.name)
			else:				
				print "ERROR - Symbol "+self.name+" not found. Line "+str(self.startLine)+"."
			return
		
		whichBlock = self.containingBlock
		while not (self.name in whichBlock.variableTable):
			if whichBlock.containingBlock is None:
				self.id = -1
				return				
			whichBlock = whichBlock.containingBlock
		self.id = (whichBlock.variableTable[self.name]).id
		
		# we keep a reference to the type of the variable that this expression
		# references
		self.type = whichBlock.variableTable[self.name].type
		
	def getType(self, containingClass):
		return self.type
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# This function will set the result register of this expression
		# to the register that currently represents the variable that
		# this expression is associated with. Note that a variable expression
		# is NOT the same thing as a field access or method call. This means
		# that this expression represents a local or formal variable or a
		# class literal.
		if (self.isClassLiteral):
			# If a variable expression is a class literal
			# then the compiler when producing AMI code
			# will use the static area pointer
			# which is kept in a register denoted sap.
			# Thus the result register after evaluating
			# the variable expression is 'sap'
			self.resultReg = "sap"
			return ""
		else:
			# return the appropriate register
			# in order to return the correct register we search
			# each containing block until we find a match and the variable
			# object in the AST will have the register name stored
			# the register that the variable is stored in is computed and
			# stored during the initial steps of AMI generation
			# this approach shouldn't fail unless there is an
			# error in the earlier phases of compilation
			whichBlock = self.containingBlock
			while not (self.name in whichBlock.variableTable):
				if whichBlock.containingBlock is None:
					print "ERROR - An earlier phase of compilation has failed!!"
					return				
				whichBlock = whichBlock.containingBlock
			whichReg = (whichBlock.variableTable[self.name]).currentRegister
			self.resultReg = whichReg			
			return ""
		
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
		
	def getType(self, containingClass):		
		# type is defined by the used operator
		# if the operand doesn't match the operator then
		# the expression isn't type correct and the type is "ERROR"
		if (self.type is None):
			if(self.operator == "!"):
				if(self.operand.getType(containingClass).whichType == "BOOLEAN"):
					self.type = TypeRecord("BOOLEAN")
				else:
					# operand-operator type mismatch
					print "ERROR - Operand-operator mismatch. Line "+str(self.startLine)+"."
					self.type = TypeRecord("ERROR")
			elif(self.operator == "-" or self.operator == "+"):
				if(self.operand.getType(containingClass).whichType == "INT"):
					self.type = TypeRecord("INT")
				elif(self.operand.getType(containingClass).whichType == "FLOAT"):
					self.type = TypeRecord("FLOAT")
				else:
					print "ERROR - Operand-operator mismatch. Line "+str(self.startLine)+"."
					self.type = TypeRecord("ERROR")
					
		return self.type
					
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# generates a new temporary register and places the result of the
		# operation in that register as well generates the AMI instructions
		# associated with said operation
		
		if(self.operator == "!"):
			# generate the code for the unary expression
			s = self.operand.getAMI(containingClass, declaration, breakLabel, continueLabel)
			if (s != ""):
				s += "\n"
						
			# get a new register
			declaration.tempRegCounter += 1
			self.resultReg = "t"+str(declaration.tempRegCounter)
			
			# using the result register we can generate code that will flip
			# the boolean value
			# but first we will need two labels
			declaration.branchCounter += 1
			labelx = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			declaration.branchCounter += 1
			labely = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			
			# essentially an if then else construct that will return a
			# flipped boolean value
			s += "bz "+self.operand.resultReg+", "+labelx + "\n"
			s += "move_immediate_i "+self.resultReg+", 0\n"
			s += "jump "+labely+"\n"
			s += labelx+":\n"
			s += "move_immediate_i "+self.resultReg+", 1\n"
			s += labely+":"
			return s
			
		elif(self.operator == "-" or self.operator == "+"):
			
			# the + operator doesn't actually do anything...
			# the - operator on the other hand negates the value
			# of the expression
			
			# get two new registers
			declaration.tempRegCounter += 1
			tempReg = "t"+declaration.tempRegCounter
			
			declaration.tempRegCounter += 1
			self.resultReg = "t"+str(declaration.tempRegCounter)
						
			# generate the code for the unary expression
			s = self.operand.getAMI(containingClass, declaration, breakLabel, continueLabel) + "\n"
			
			# generate the code to flip the value of the expression
			s += "move_immediate_i "+tempReg+", 0\n"
			s += "isub "+self.resultReg+", "+tempReg+", "+self.operand.resultReg
			return s
			
	
		
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
		
	def getType(self, containingClass):
		# Type checking must be performed post AST construction. In particular,
		# we cannot know the subclass structure until we have processed all of
		# the classes!
		if (self.type is None):
			# type is defined by the used operator
			# if the operand doesn't match the operator then
			# the expression isn't type correct and the type is "ERROR"
			if (self.operator == "+" or
				self.operator == "-" or
				self.operator == "*" or
				self.operator == "/"):
				if(self.operand1.getType(containingClass).whichType == "INT" and
				   self.operand2.getType(containingClass).whichType == "INT"):
					self.type = TypeRecord("INT")
				elif(self.operand1.getType(containingClass).whichType == "FLOAT" and
					 self.operand2.getType(containingClass).whichType == "FLOAT"):
					self.type = TypeRecord("FLOAT")
				else:
					print "ERROR - Operand-operator mismatch. Line "+str(self.startLine)+"."
					self.type = TypeRecord("ERROR")
			elif(self.operator == "&&" or
				 self.operator == "||"):
				if(self.operand1.getType(containingClass).whichType == "BOOLEAN" and
				   self.operand2.getType(containingClass).whichType == "BOOLEAN"):
					self.type = TypeRecord("BOOLEAN")
				else:
					print "ERROR - Operand-operator mismatch. Line "+str(self.startLine)+"."
					self.type = TypeRecord("ERROR")
			elif(self.operator == "<" or
				 self.operator == "<=" or
				 self.operator == ">" or
				 self.operator == ">="):
				if(self.operand1.getType(containingClass).whichType == "INT" and
				   self.operand2.getType(containingClass).whichType == "INT"):
					self.type = TypeRecord("BOOLEAN")
				elif(self.operand1.getType(containingClass).whichType == "FLOAT" and
					 self.operand2.getType(containingClass).whichType == "FLOAT"):
					self.type = TypeRecord("BOOLEAN")
				else:
					print "ERROR - Operand-operator mismatch. Line "+str(self.startLine)+"."
					self.type = TypeRecord("ERROR")
			elif(self.operator == "==" or
				 self.operator == "!="):
				if(self.operand1.getType(containingClass).isSubType(self.operand2.getType(containingClass)) or
				   self.operand2.getType(containingClass).isSubType(self.operand1.getType(containingClass))):
					self.type = TypeRecord("BOOLEAN")
				else:
					print "ERROR - Operand-operator mismatch. Line "+str(self.startLine)+"."
					self.type = TypeRecord("ERROR")
					
		return self.type
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		# evaluation of the binary expression tree uses post-order
		# traversal
		
		# generate code for left subtree and get the resulting register
		s = self.operand1.getAMI(containingClass, declaration, breakLabel, continueLabel)
		if(s != ""):
			s += "\n"
		r1 = self.operand1.resultReg
		
		# generate code for right subtree and get the resulting register
		temp = self.operand2.getAMI(containingClass, declaration, breakLabel, continueLabel)
		if(temp != ""):
			s += temp + "\n"
		r2 = self.operand2.resultReg
		
		# get a new register
		declaration.tempRegCounter += 1
		self.resultReg = "t"+str(declaration.tempRegCounter)
		
		if (self.operator == "+" or
			self.operator == "-" or
			self.operator == "*" or
			self.operator == "/" or
			self.operator == "<" or
			self.operator == "<=" or
			self.operator == ">" or
			self.operator == ">="):
		
			# dealing with ints or floats as operands
			# determine which type
			# we assume all expressions are correctly typed by now
			intArith = (self.operand1.type.whichType == "INT")
				
			if (self.operator == "+"):
				if (intArith):
					s += "iadd "+self.resultReg+", "+r1+", "+r2
				else:
					s += "fadd "+self.resultReg+", "+r1+", "+r2					
			elif(self.operator == "-"):
				if (intArith):
					s += "isub "+self.resultReg+", "+r1+", "+r2
				else:
					s += "fsub "+self.resultReg+", "+r1+", "+r2				
			elif(self.operator == "*"):
				if (intArith):
					s += "imul "+self.resultReg+", "+r1+", "+r2
				else:
					s += "fmul "+self.resultReg+", "+r1+", "+r2				
			elif(self.operator == "/"):
				if (intArith):
					s += "idiv "+self.resultReg+", "+r1+", "+r2
				else:
					s += "fdiv "+self.resultReg+", "+r1+", "+r2							
			elif(self.operator == "<"):
				if (intArith):
					s += "ilt "+self.resultReg+", "+r1+", "+r2
				else:
					s += "flt "+self.resultReg+", "+r1+", "+r2				
			elif(self.operator == "<="):
				if (intArith):
					s += "ileq "+self.resultReg+", "+r1+", "+r2
				else:
					s += "fleq "+self.resultReg+", "+r1+", "+r2	
			elif(self.operator == ">"):
				if (intArith):
					s += "igt "+self.resultReg+", "+r1+", "+r2
				else:
					s += "fgt "+self.resultReg+", "+r1+", "+r2
			elif(self.operator == ">="):
				if (intArith):
					s += "igeq "+self.resultReg+", "+r1+", "+r2
				else:
					s += "fgt "+self.resultReg+", "+r1+", "+r2
					
		elif(self.operator == "&&"):
			# we return 1 if both r1 and r2 are equal to 1
			# and return 0 in any other case
			# we'll create some labels to make this easier
			declaration.branchCounter += 1
			failure = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			declaration.branchCounter += 1
			success = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			declaration.branchCounter += 1
			finish = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			
			s += "bz "+r1+", "+failure + "\n"
			s += "bz "+r2+", "+failure + "\n"
			s += "jump "+success + "\n"
			s += failure+":\n"
			s += "move_immediate_i "+self.resultReg+", 0\n"
			s += "jump "+ finish + "\n"
			s += success+":\n"
			s += "move_immediate_i "+self.resultReg+", 1\n"
			s += finish+":"					
		elif(self.operator == "||"):
			# we return 1 if either r1 or r2 are equal to 1
			# and return 0 in any other case
			# we'll create some labels to make this easier
			declaration.branchCounter += 1
			failure = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			declaration.branchCounter += 1
			success = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			declaration.branchCounter += 1
			finish = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			
			s += "bnz "+r1+", "+success + "\n"
			s += "bnz "+r2+", "+success + "\n"
			s += "jump "+failure + "\n"
			s += failure+":\n"
			s += "move_immediate_i "+self.resultReg+", 0\n"
			s += "jump "+ finish + "\n"
			s += success+":\n"
			s += "move_immediate_i "+self.resultReg+", 1\n"
			s += finish+":"		

		elif(self.operator == "=="):
			
			# since all we have are integers or floats to work with
			# we just convert any floats to int and branch on the difference
			# we should do something smarter here but I'm not sure how I would
			# handle branch on zero if the branch statement only takes an int
			# argument
						
			# get new registers
			declaration.tempRegCounter += 1
			temp1 = "t"+str(declaration.tempRegCounter)
			declaration.tempRegCounter += 1
			temp2 = "t"+str(declaration.tempRegCounter)
			declaration.tempRegCounter += 1
			temp3 = "t"+str(declaration.tempRegCounter)
			
			if(self.operand1.type.whichType == "FLOAT"):				
				s+= "ftoi "+temp1+", "+r1+"\n"			
			else:
				s+= "move "+temp1+", "+r1+"\n"
			if(self.operand2.type.whichType == "FLOAT"):								
				s+= "ftoi "+temp2+", "+r2+"\n"		
			else:
				s+= "move "+temp2+", "+r2+"\n"
			
			# now get a few labels
			declaration.branchCounter += 1
			failure = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			declaration.branchCounter += 1
			success = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			declaration.branchCounter += 1
			finish = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			
			s += "isub "+temp3+", "+temp1+", "+temp2+"\n"
			s += "bz "+temp3+", "+success + "\n"
			s += "jump "+failure + "\n"
			s += failure+":\n"
			s += "move_immediate_i "+self.resultReg+", 0\n"
			s += "jump "+ finish + "\n"
			s += success+":\n"
			s += "move_immediate_i "+self.resultReg+", 1\n"
			s += finish+":"	
			
		elif(self.operator == "!="):
		
			# we do almost exactly the same thing for this operator
			# as for == except we change bz to bnz
			
			# get new registers
			declaration.tempRegCounter += 1
			temp1 = "t"+declaration.tempRegCounter
			declaration.tempRegCounter += 1
			temp2 = "t"+declaration.tempRegCounter
			declaration.tempRegCounter += 1
			temp3 = "t"+declaration.tempRegCounter
			
			if(operand1.type.whichType == "FLOAT"):				
				s+= "ftoi "+temp1+", "+r1+"\n"			
			else:
				s+= "move "+temp1+", "+r1+"\n"
			if(operand2.type.whichType == "FLOAT"):								
				s+= "ftoi "+temp2+", "+r2+"\n"		
			else:
				s+= "move "+temp2+", "+r2+"\n"
			
			# now get a few labels
			declaration.branchCounter += 1
			failure = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			declaration.branchCounter += 1
			success = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			declaration.branchCounter += 1
			finish = declaration.getAMILabel()+"_"+str(declaration.branchCounter)
			
			s += "isub "+temp3+", "+temp1+", "+temp2+"\n"
			s += "bnz "+temp3+", "+success + "\n"
			s += "jump "+failure + "\n"
			s += failure+":\n"
			s += "move_immediate_i "+self.resultReg+", 0\n"
			s += "jump "+ finish + "\n"
			s += success+":\n"
			s += "move_immediate_i "+self.resultReg+", 1\n"
			s += finish+":"
			
		return s
		
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
		s += ", " + self.leftHandSide.type.whichType
		s += ", " + self.rightHandSide.type.whichType
		s += " )"
		return s
		
	def getType(self, containingClass):
		if (self.type is None):
			rhs = self.rightHandSide.getType(containingClass)			
			lhs = self.leftHandSide.getType(containingClass) 
			if (rhs.isSubType(lhs)
				and rhs.whichType != "ERROR"
				and lhs.whichType != "ERROR"):
				self.type = rhs
			else:
				print "ERROR - Assignment Error. Line "+str(self.startLine)+"."
				self.type = TypeRecord("ERROR")
		return self.type
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		
		# we must evaluate the lefthandside and use the register that
		# results
		s = self.leftHandSide.getAMI(containingClass, declaration, breakLabel, continueLabel)
		if(s != ""):
			s += "\n"
		leftReg = self.leftHandSide.resultReg
		
		# similarly we must get the register that results from evaluating
		# the righthandside
		temp = self.rightHandSide.getAMI(containingClass, declaration, breakLabel, continueLabel)
		if(temp != ""):
			s += temp + "\n"
		rightReg = self.rightHandSide.resultReg
		
		# then we move the righthandside into the lefthandside
		# in the case that the left hand side represents
		# a FieldAccessExpression we must use a heap store
		# as opposed to a move instruction
		if(isinstance(self.leftHandSide, FieldAccessExpression)):
			address, offset = self.leftHandSide.resultAO
			s += "hstore "+address+", "+offset+", "+rightReg
		else:
			s += "move "+leftReg+", "+rightReg
		
		return s
		
class AutoExpression:

	def __init__(self, operand, incOrDec, postOrPre, startLine, endLine):
		self.operand = operand
		self.incOrDec = incOrDec
		self.postOrPre = postOrPre
		self.startLine = startLine
		self.endLine = endLine
		self.type = None
				
	def toString(self):
		s = "AutoExpr( "
		s += self.operand.toString() + ", "
		s += self.incOrDec + ", "
		s += self.postOrPre
		s += " )"
		return s
		
	def getType(self, containingClass):
		if(self.type is None):
			if(self.operand.getType(containingClass).whichType == "INT"):
				self.type = TypeRecord("INT")
			elif(self.operand.getType(containingClass).whichType == "FLOAT"):
				self.type = TypeRecord("FLOAT")
			else:
				print "ERROR - Operand-operator mismatch, auto expression must be either int or float. Line "+str(self.startLine)+"."
				self.type = TypeRecord("ERROR")
		return self.type
		
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		if(self.type.whichType == "INT"):
			type = "i"
		elif(self.type.whichType == "FLOAT"):
			type = "f"
		
		if(self.incOrDec == "increment"):
			val = "1"
		else:
			val = "-1"			
		
		# get a new temporary register to store the
		# result of the expression
		declaration.tempRegCounter += 1
		self.resultReg = "t"+str(declaration.tempRegCounter)
		
		s = self.operand.getAMI(containingClass, declaration, breakLabel, continueLabel)
		if(self.postOrPre == "post"):
			s += "move "+self.resultReg+", "+self.operand.resultReg+"\n"
				
		# get a new temporary register to
		# perform the operation
		declaration.tempRegCounter += 1
		tempReg = "t"+str(declaration.tempRegCounter)
		
		# perform the operation on the operand
		s += "move_immediate_"+type+" "+tempReg+", "+val+"\n"
		s += type+"add "+self.operand.resultReg+", "+self.operand.resultReg+", "+tempReg
		
		if(isinstance(self.operand, FieldAccessExpression)):
			# in the case that the operation is performed
			# on a field access then we must store the result in
			# the heap
			address, offset = self.operand.resultAO
			s += "\nhstore "+address+", "+offset+", "+self.operand.resultReg
			
		if(self.postOrPre == "pre"):
			s += "\nmove "+self.resultReg+", "+self.operand.resultReg
			
		return s
		
			
	
class FieldAccessExpression:

	def __init__(self, base, name, startLine, endLine):
		self.base = base
		self.name = name
		self.startLine = startLine
		self.endLine = endLine
		self.type = None
			
	def toString(self):
		s = "FieldAccess( "
		if not (self.base is None):
			if isinstance(self.base, str):
				s += self.base+", "
			else:
				s += self.base.toString() + ", "
		s += self.name
		s += ", "
		s += str(self.id)
		s += " )"
		return s
	
	# Useful method to help shorten name resolution code
	# Searches all of the superclasses of the base class until a public
	# field that matches the name parameter as well as the 
	# applicability parameter is found and returned
	# Upon failure, 'None' is returned
	def searchSuperClassesForField(self, baseClassType, applicability, name):	
		if(baseClassType in DecafClass.classes):
			search = DecafClass.classes[baseClassType]
		else:
			return None
		
		if(search.superName is None):
			return None
		
		if not (search.superName in DecafClass.classes):
			return None
		
		x = DecafClass.classes[search.superName]	
		loop = True
		resolve = None
		while(loop):
			# search the field table for the name
			for i in range(0, len(x.fieldTable)):
				if(x.fieldTable[i].visibility == "public"
					and x.fieldTable[i].name == name
					and x.fieldTable[i].applicability == applicability):
					resolve = x.fieldTable[i]
					loop = False
					break
		
			# if the field table doesn't contain the name
			# then we search the super class																
			# but if there is no super class, then we break the
			# loop
			if ( not (x.superName is None) 
				and (x.superName in DecafClass.classes)):
				x = DecafClass.classes[x.superName]
			else:
				loop = False
				
		# upon exiting the while loop, we either have successfully
		# resolved the name or not
		return resolve
	
	# This method will return a field record by searching the AST using the
	# base and name values of this expression.
	# The approach is to begin at the base class and using its definition
	# check whether or not a visible field matches the name value of this 
	# expression.
	# If a visible field is not found, then each superclass of the given
	# base class is checked sequentially in the same way.
	# If no field is found after searching all superclasses then name
	# resolution has failed and 'None' is returned signalling failure.
	def nameResolution(self, containingClass):
		
		# if the base class is a built-in type then an error is present	
		if( not isinstance(self.base, ThisExpression) and self.base.type.isBuiltIn()):
			return None
		
		# the algorithm is slightly different if we're dealing directly with
		# a 'ThisExpression'
		if isinstance(self.base, ThisExpression):
			# resolving an attribute name
			x = containingClass
			for i in range(0, len(x.fieldTable)):
				if(x.fieldTable[i].name == self.name							
					and x.fieldTable[i].applicability == "instance"):
					return x.fieldTable[i]
			# if the field isn't found in the immediate class
			# then we search each successive superclass for a visible
			# field
			return self.searchSuperClassesForField(x.name, "instance", self.name)
		elif( isinstance(self.base, VariableExpression) and self.base.isClassLiteral):
			# the algorithm also changes a bit when you're dealing with
			# a class literal
			cType = self.base.type.whichType
			x = DecafClass.classes[cType]			
			# resolving a static attribute name
			for i in range(0, len(x.fieldTable)):
				if(x.fieldTable[i].name == self.name							
					and x.fieldTable[i].applicability == "static"):
					return x.fieldTable[i]
			# if the field isn't found in the immediate class
			# then we search each successive superclass for a visible
			# field
			return self.searchSuperClassesForField(cType, "static", self.name)
		else:
			# in all other cases we use the type of the base expression
			# and use that to execute name resolution
			cType = self.base.getType(containingClass).whichType
			x = DecafClass.classes[cType]
			# resolving an attribute name
			for i in range(0, len(x.fieldTable)):
				if(x.fieldTable[i].name == self.name							
					and x.fieldTable[i].applicability == "instance"):
					return x.fieldTable[i]
					
			# if the field isn't found in the immediate class
			# then we search each successive superclass for a visible
			# field
			
			return self.searchSuperClassesForField(cType, "instance", self.name)
	
	def getType(self, containingClass):
		# if the base is a class name as opposed to a variable that
		# has a class type then the base ought to be considered a class
		# literal
		# we will also need to perform name resolution on the given name
		# note that we need only the type of the resolved name as opposed
		# to the actual variable
		
		if(self.type is None):
			# perform name resolution and set the type to the
			# type of the returned field record
			check = self.nameResolution(containingClass)
			if (check is None):
				print "ERROR - Field with name "+self.name+" could not be found. Line "+str(self.startLine)+"."
				self.type = TypeRecord("ERROR")
			else:
				self.id = check.id
				self.type = check.type
		
		return self.type
		
	# Field access expressions in the context of this compiler
	# explicitly represent attributes of a particular base
	# object (or represent a static field access)
	# and although field access expressions overlap
	# with method call expressions in the attribute grammar it
	# is the case that field access expression objects created
	# during the creation of method call expressions are
	# unreachable within the AST.
	# Thus the AMI for a field expression begins with evaluating
	# the base expression and proceeds to use the result to
	# get a pointer to the object record that corresponds to the
	# evaluated expression and finally the offset of the 'name'
	# attribute is determined and used to properly access the
	# heap and retrieve the correct address
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
	
		# evaluation of this expression is almost entirely
		# different in the case that the base expression actually
		# denotes a static field access
		s = ""
		if (isinstance(self.base, VariableExpression)
			and self.base.isClassLiteral):
			
			# to start, name resolution will yield the
			# relevant field record			
			field = self.nameResolution(containingClass)
			
			# We must determine the
			# offset of each static field with respect to the
			# static area pointer
			# all of the static data is placed in one area
			# and it doesn't matter all that much how the
			# offsets are organized as long as the offsets
			# are used consistently
			# this means that we can assign a new offset
			# to a static field as it is added to the AST
			# and use that offset here when we need it
				
			# at this point we should have the correct offset
			# for the field and can generate the AMI to load
			# the field
			
			# get a new temporary register to place the
			# accessed value in
			declaration.tempRegCounter += 1
			self.resultReg = "t"+str(declaration.tempRegCounter)
			
			# get another temp register to handle the offset
			declaration.tempRegCounter += 1
			offsetReg = "t"+str(declaration.tempRegCounter)
			
			# place the offset into a register
			s += "move_immediate_i "+offsetReg+", "+str(field.staticOffset)+"\n"
			
			# return the address and offset pair as a tuple
			self.resultAO = ("sap", offsetReg)
			
			# access the field in the static data area
			# and move the result to
			# the result register
			s += "hload "+self.resultReg+", sap, " + offsetReg
			
			return s
			
		# in the case that we're dealing with a
		# non-static field access...
		
		s += self.base.getAMI(containingClass, declaration, breakLabel, continueLabel)		
		
		# How do we know what the offset of a field is?
		# We can use name resolution to determine the
		# field record that this expression refers to except
		# we need to derive the offset of the field with respect
		# to the class that contains it
		# Part of the problem is that if the class that
		# contains the field
		# is a base class then we can walk through the field table
		# one field at a time to determine the field offset
		# In the case that the field belongs to a subclass
		# then we will need to add to the offset the size of the
		# field table for each super class
		field = self.nameResolution(containingClass)
		
		# walk the field table of the class that contains
		# the field
		whichClass = DecafClass.classes[field.containingClass]
		tableSize = len(whichClass.fieldTable)
		offset = 0
		for i in range(0, tableSize):
			if(field == whichClass.fieldTable[i]):
				break
			else:
				offset += 1
				
		# add offsets for all non-static fields of superclasses
		superClassName = whichClass.superName
		while( not superClassName is None and superClassName != ""):
			# get the super class
			superClass = DecafClass.classes[superClassName]
			# add the size of the super class field table
			# to the offset without including static fields
			for x in superClass.fieldTable:
				if(x.applicability == "instance"):
					offset += 1
			# get the name of the next super class
			superClassName = superClass.superName
			
		# at this point we should have the correct offset
		# for the field and can generate the AMI to load
		# the field from the object record
		
		# The next problem we have is that contextually we
		# don't know if we want to return the address
		# and offset pair that represents this field access
		# or if we simply wish to return the value of the field
		# access. We may need to return both!		
		# Since we cannot know if we need both then
		# we return both everytime in .resultReg and
		# .resultAO
		
		# get a new temporary register to place the
		# accessed value in
		declaration.tempRegCounter += 1
		self.resultReg = "t"+str(declaration.tempRegCounter)
		
		# get another temp register to handle the offset
		declaration.tempRegCounter += 1
		offsetReg = "t"+str(declaration.tempRegCounter)
		
		# place the offset into a register
		s += "move_immediate_i "+offsetReg+", "+str(offset)+"\n"
		
		# return the address and offset pair as a tuple
		self.resultAO = (self.base.resultReg, offsetReg)
		
		# The result register of the base is expected to
		# contain the address of an object record
		# and name resolution has been used to determine the 
		# offset of the named attribute
		
		# access the object record on the heap
		# and move the result to
		# the result register
		s += "hload "+self.resultReg+", "+self.base.resultReg +", " + offsetReg
				
		return s
	
class MethodCallExpression:

	def __init__(self, base, name, args, startLine, endLine):
		self.base = base
		self.name = name
		self.args = args
		self.startLine = startLine
		self.endLine = endLine
		self.type = None
			
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
			s += self.args[len(self.args)-1].toString()+" \n"			
		s += "])"
		s += ", "
		s += str(self.id)
		s += " )"
		return s
		
	# Useful method to help shorten name resolution code
	# Searches all of the superclasses of the base class until a public
	# method that matches the method parameter as well as the 
	# applicability parameter is found and returned
	# Note that matching a method requires a bit more detail
	# than matching a field name and here we do NOT check that
	# the argument expressions are type correct
	# Upon failure, 'None' is returned
	def searchSuperClassesForMethod(baseClassType, applicability, methodName, methodParameters):	
		if(baseClassType in DecafClass.classes):
			search = DecafClass.classes[baseClassType]
		else:
			return None
		
		if(search.superName is None):
			return None
		
		if not (search.superName in DecafClass.classes):
			return None
		
		x = DecafClass.classes[search.superName]	
		loop = True
		resolve = None
		while(loop):
			# search the method table for the name
			# note that for CSE 304 we do not worry about method
			# overloading so this part of the code is somewhat simplified
			for i in range(0, len(x.methodTable)):
				if(x.methodTable[i].visibility == "public"
					and x.methodTable[i].name == name
					and x.methodTable[i].applicability == applicability):
					resolve = x.methodTable[i]
					# ensure that the method makes sense, specifically 
					# that each actual parameter is a subtype of each
					# respective formal parameter					
					if(len(resolve.parameters) != len(methodParameters)):
						resolve = None
					else:
						for j in range(0, len(resolve.parameters)):
							if not (methodParameters[j].type.isSubType(resolve.parameters[j].type)):
								resolve = None
					
					# if we find a method then we break the loop
					if not (resolve is None):
						loop = False
						break
		
			# if the field table doesn't contain the name
			# then we search the super class																
			# but if there is no super class, then we break the
			# loop
			if ( not (x.superName is None) 
				and (x.superName in DecafClass.classes)):
				x = DecafClass.classes[x.superName]
			else:
				loop = False
				
		# upon exiting the while loop, we either have successfully
		# resolved the name or not
		return resolve
		
	# This method will return a method record by searching the AST using the
	# base and args values of this expression.
	# The approach is to begin at the base class and using its definition
	# check whether or not a visible method matches the name and args values
	# of this expression.
	# If an applicable method is not found, then each superclass of the given
	# base class is checked sequentially in the same way.
	# If no method is found after searching all superclasses then name
	# resolution has failed and 'None' is returned signalling failure.
	def nameResolution(self, containingClass):
				
		# if the base class is a built-in type then an error is present
		if( not isinstance(self.base, ThisExpression) and self.base.getType(containingClass).isBuiltIn()):
			return None
		
		# the algorithm is slightly different if we're dealing directly with
		# a 'ThisExpression'
		if isinstance(self.base, ThisExpression):
			# resolving a method name
			x = containingClass
			for i in range(0, len(x.methodTable)):
				if(x.methodTable[i].name == self.name							
					and x.methodTable[i].applicability == "instance"):
					resolve = x.methodTable[i]
					# ensure that the method makes sense, specifically 
					# that each actual parameter is a subtype of each
					# respective formal parameter					
					if(len(resolve.parameters) != len(self.args)):
						resolve = None
					else:
						for j in range(0, len(resolve.parameters)):
							if not (self.args[j].type.isSubType(resolve.parameters[j].type)):
								resolve = None
						
					# if we find a method then we return it
					if not (resolve is None):
						return resolve
										
			# if the field isn't found in the immediate class
			# then we search each successive superclass for a visible
			# method
			return searchSuperClassesForMethod(x.name, "instance", self.name, self.args)
		elif( isinstance(self.base, VariableExpression) and self.base.isClassLiteral):
			# the algorithm also changes a bit when you're dealing with
			# a class literal
			cType = self.base.type.whichType
			x = DecafClass.classes[cType]			
			# resolving a method name
			for i in range(0, len(x.methodTable)):
				if(x.methodTable[i].name == self.name							
					and x.methodTable[i].applicability == "static"):
					resolve = x.methodTable[i]
					# ensure that the method makes sense, specifically 
					# that each actual parameter is a subtype of each
					# respective formal parameter					
					if(len(resolve.parameters) != len(self.args)):
						resolve = None
					else:
						for j in range(0, len(resolve.parameters)):
							if not (self.args[j].type.isSubType(resolve.parameters[j].type)):
								resolve = None
						
					# if we find a method then we return it
					if not (resolve is None):
						return resolve
			# if the method isn't found in the immediate class
			# then we search each successive superclass for a visible
			# method
			return searchSuperClassesForMethod(cType, "static", self.name, self.args)
		else:
			# in all other cases we use the type of the base expression
			# and use that to execute name resolution
			cType = self.base.getType(containingClass).whichType
			x = DecafClass.classes[cType]			
			# resolving a method name
			for i in range(0, len(x.methodTable)):
				if(x.methodTable[i].name == self.name							
					and x.methodTable[i].applicability == "instance"):
					resolve = x.methodTable[i]
					# ensure that the method makes sense, specifically 
					# that each actual parameter is a subtype of each
					# respective formal parameter
					if(len(resolve.parameters) != len(self.args)):
						resolve = None
					else:
						for j in range(0, len(resolve.parameters)):
							if not (self.args[j].type.isSubType(resolve.parameters[j].type)):
								resolve = None
						
					# if we find a method then we return it
					if not (resolve is None):
						return resolve
						
			# if the method isn't found in the immediate class
			# then we search each successive superclass for a visible
			# method
			return searchSuperClassesForMethod(cType, "instance", self.name, self.args)
	
	def getType(self, containingClass):
		
		if(self.type is None):
		
			# in order to determine the type of this expression
			# we must first ensure that all of the expressions found in the
			# arguments list are not "ERROR" (that is, they are type correct)
			argsTypeCorrect = True
			for i in range(0, len(self.args)):
				if(self.args[i].getType(containingClass).whichType == "ERROR"):
					argsTypeCorrect = False
			
			if not argsTypeCorrect:
				print "ERROR - A method argument isn't type correct. Line "+str(self.startLine)+"."
				return TypeRecord("ERROR")
			
			
			# now that we know the arguments are type correct we can proceed
			# to perform name resolution and set the type to the
			# type of the returned method record's declared return type
			check = self.nameResolution(containingClass)
			if (check is None):
				print "ERROR - A method with the name "+self.name+" could not be found. Line "+str(self.startLine)+"."
				self.type = TypeRecord("ERROR")
			else:
				self.id = check.id
				self.type = check.returnType
		
		return self.type
	
	# Returns AMI for this method call as a string
	# Method calls make use of the control stack to save and
	# restore registers
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		
		# the first order of business translating
		# a method call to AMI is to use name resolution
		# to find the method record in the AST that this
		# method call refers to		
		method = self.nameResolution(containingClass)
		
		# we also need to keep track of the registers that
		# are to be restored after the method returns
		
		# Saving registers gets a bit complicated....
		# In order to be absolutely certain that the registers
		# used in the caller aren't overwritten upon returning
		# to the caller we must save all of them on the call
		# stack
		# How do we know which registers to save?
		# We must save all of the argument registers of the
		# caller as well as all of the temporary registers
		# of the caller. These correspond to the local and
		# formal variables of the caller.
		# Each variable must then be popped off the control
		# stack after the method returns.
		savedArgRegs = 0		
		argumentCounter = 0 # this variable will be used later
		s = ""
		# which registers are manipulated also depends
		# on whether the called method is static or instance
		# as the first register will hold the 
		# implicit 'this' object for an instance method
		# In any of these three cases we must save the
		# a0 register
		isThisExpression = isinstance(self.base, ThisExpression)
		if (declaration.applicability == "instance"):			
			s += "save a0\n"
			savedArgRegs += 1
		elif(method.applicability == "instance"
			and not isThisExpression):			
			s += "save a0\n"
			savedArgRegs += 1
		elif(isThisExpression):
			s += "save a0\n"
			savedArgRegs += 1
			
		# In this case we must properly set the a0
		# register
		if(method.applicability == "instance"
			and not isThisExpression):	
			# Move 'this' into a0
			# How do we get 'this'? 'this' is represented as
			# an address to a location on the heap
			# Where can we find that address?
			# That address should be accessible after
			# resolving the base expression as the base
			# expression represents the instance object
			# that owns the method
			
			# resolve the expression and use the address of the
			# class instance
			t = self.base.getAMI(containingClass, declaration, breakLabel, continueLabel)
			s += t
			if (t != ""):
				s += "\n"
			addressReg, offset = self.base.resultAO
			s += "move a0, "+addressReg+"\n"
			argumentCounter = 1			
					
		# for each argument of the calling method
		# we save another register on the control stack
		temp = declaration.block.variableTable
		for x in temp.keys():
			if (temp[x].localOrFormal == "formal"):
				s += "save a"+str(savedArgRegs)+"\n"
				savedArgRegs += 1
				
		# Every temporary register used in the declaration
		# up to this point must be saved on the control stack
		for i in range(0, declaration.tempRegCounter+1):
			s += "save t"+str(i)+"\n"
	
		# keep track of the number of saved registers
		savedTempRegs = declaration.tempRegCounter
	
		# for each argument replace the current argument register		
		# with the contents of the register retrieved after resolving
		# the argument expression
		for i in range(0, len(self.args)):
			t = self.args[i].getAMI(containingClass, declaration, breakLabel, continueLabel)
			s += t
			if(t != ""):
				s += "\n"
			s += "move a"+str(argumentCounter)+", "+self.args[i].resultReg+"\n"
			argumentCounter += 1
			
		# now that the pre-call state has been setup
		# appropriately we can jump to the method label
		# we use a "call" instruction to properly make
		# use of the control stack
		s += "call "+method.getAMILabel()
		
		# after the call returns but before we restore
		# argument registers we want to ensure that we
		# communicate the return value of the called
		# method
		# generate a temporary register and use it
		# to store the return value
		declaration.tempRegCounter += 1
		self.resultReg = "t"+str(declaration.tempRegCounter)
		s += "\nmove "+self.resultReg+", a0"
		
		# after the call returns we restore each argument
		# register as well as each temporary register
		# to their pre-call states
		# (excluding the last temporary register)
		for i in range(savedTempRegs, -1, -1):
			s += "\nrestore t"+str(i)
			
		for i in range(savedArgRegs-1, -1, -1):
			s += "\nrestore a"+str(i)
		
		return s
		
	
class NewObjectExpression:

	def __init__(self, base, args, startLine, endLine):
		self.base = base
		self.args = args
		self.startLine = startLine
		self.endLine = endLine
		self.type = None
		
	def toString(self):
		s = "NewObject( "		
		if not (self.base is None):
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
		s += ", "
		s += str(self.id)
		s += " )"
		return s
		
	# Name resolution for constructors is relatively straightforward since
	# we do not need to search superclasses in the AST in comparison to
	# name resolution for either methods or fields
	def nameResolution(self, containingClass):
		
		# We use the name of the class that we're constructing
		# to execute name resolution
		cType = self.base
		if not (cType in DecafClass.classes):
			return None
		x = DecafClass.classes[cType]
		
		# resolving a constructor
		for i in range(0, len(x.constructorTable)):
			if(x.constructorTable[i].name == self.base):
				# I'm not entirely certain how constructors are supposed
				# to work with visibility and applicability, that is I don't
				# know what is meant by a static constructor or a private
				# constructor. This isn't elaborated on in the manual either.
				resolve = x.constructorTable[i]
				# ensure that the constructor makes sense, specifically 
				# that each actual parameter is a subtype of each
				# respective formal parameter
				if(len(resolve.parameters) != len(self.args)):
					resolve = None
				else:
					for j in range(0, len(resolve.parameters)):
						if not (self.args[j].type.isSubType(resolve.parameters[j].type)):
							resolve = None
					
				# if we find a constructor then we return it
				if not (resolve is None):
					return resolve
					
		# if the constructor isn't found in the immediate class
		# then we return 'None' to signify an error
		return None
	
	def getType(self, containingClass):
		
		if(self.type is None):
		
			# in order to determine the type of this expression
			# we must first ensure that all of the expressions found in the
			# arguments list are not "ERROR" (that is, they are type correct)
			argsTypeCorrect = True
			for i in range(0, len(self.args)):
				if(self.args[i].getType(containingClass).whichType == "ERROR"):
					argsTypeCorrect = False
			
			if not argsTypeCorrect:
				print "ERROR - A constructor argument isn't type correct. Line "+str(self.startLine)+"."
				return TypeRecord("ERROR")
						
			# now that we know the arguments are type correct we can proceed
			# to perform name resolution and set the type to the
			# name of the constructed object's class
			check = self.nameResolution(containingClass)
			if (check is None):
				print "ERROR - Constructor for class "+self.base+" could not be resolved. Line "+str(self.startLine)+"."
				self.type = TypeRecord("ERROR")
			else:
				self.id = check.id
				self.type = TypeRecord(self.base)
		
		return self.type

	# Generates the AMI code for creating a new instance
	# of an object and returns the code as a string
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		
		# To start we will need to allocate some space
		# on the heap and must know how much space to
		# allocate. This is determined by the number of instance
		# variables present in class for which a new instance
		# is being generated as well as the number of instance
		# variables of each superclass
		
		# We'll need to correctly resolve the name of the
		# constructor as well as the associated class
		# Fortunately constructors aren't overloaded for this
		# assignment so this becomes a bit easier
		whichClass = DecafClass.classes[self.base]
		constructor = self.nameResolution(containingClass)
		
		# Now we need to count the instance variables
		# of this new object
		instanceCount = 0
		for x in whichClass.fieldTable:
			if(x.applicability == "instance"):
				instanceCount += 1
		
		# We also factor in the instance variables of
		# each superclass
		superClassName = whichClass.superName
		while( not superClassName is None and superClassName != ""):
			superClass = DecafClass.classes[superClassName]				
			for x in superClass.fieldTable:
				if(x.applicability == "instance"):
					instanceCount += 1
			superClassName = superClass.superName
			
		# Now that we have all the instance variables accounted
		# for we can generate a heap allocation and store
		# the object reference in a new temporary register
		
		# generate a temporary register and
		# store the object reference in it
		declaration.tempRegCounter += 1
		objectRef = "t"+str(declaration.tempRegCounter)
		
		# generate another temporary register and
		# store the instance variable count in it
		declaration.tempRegCounter += 1
		numVars = "t"+str(declaration.tempRegCounter)
		
		s = "move_immediate_i "+numVars+", "+str(instanceCount)+"\n"
		s += "halloc "+objectRef+", "+numVars+"\n"
		
		# The result of evaluating this expression as far as the
		# compiler is concerned is the register that holds
		# the object reference
		self.resultReg = objectRef
		
		# As we have done with method calls we must
		# save all of the argument registers as well
		# as the temporary registers that correspond
		# to relevant local variables
		# before we make a call to construct an object
		savedArgRegs = 0	# these variables will be used later	
		argumentCounter = 0
		if(declaration.applicability == "instance"):
			# if the calling method is a method of an object
			# then we must ensure that we save the 'this'
			# pointer stored in the a0 register
			s += "save a0\n"
			savedArgRegs = 1	# these variables will be used later	
			argumentCounter = 1
					
		# for each argument of the calling method
		# we save another register on the control stack
		temp = declaration.block.variableTable
		for x in temp.keys():
			if (temp[x].localOrFormal == "formal"):
				s += "save a"+str(savedArgRegs)+"\n"
				savedArgRegs += 1
				
		# Every temporary register used in the declaration
		# up to this point must be saved on the control stack
		for i in range(0, declaration.tempRegCounter+1):
			s += "save t"+str(i)+"\n"
		
		# Keep track of the number of saved temporary
		# registers
		savedTempRegs = declaration.tempRegCounter
				
		# now that we have saved all of the relevant
		# registers we now save the object reference
		# register and move its contents into the
		# 'this' register or the a0 register			
		s += "move a0, "+objectRef+"\n"
	
		# for each argument replace the current argument register		
		# with the contents of the register retrieved after resolving
		# the argument expression
		for i in range(0, len(self.args)):
			t = self.args[i].getAMI(self, containingClass, declaration, breakLabel, continueLabel)
			s += t
			if(t != ""):
				s += "\n"
			s += "move a"+str(argumentCounter)+", "+self.args[i].resultReg+"\n"
			argumentCounter += 1
			
		# now that the pre-call state has been setup
		# appropriately we can jump to the method label
		# we use a "call" instruction to properly make
		# use of the control stack
		s += "call "+constructor.getAMILabel()
		
		# constructors do not return any values
		
		# after the call returns we restore each argument
		# register as well as each temporary register
		# to their pre-call states
		for i in range(savedTempRegs, -1, -1):
			s += "\nrestore t"+str(i)
			
		# now restore the argument registers
		for i in range(savedArgRegs-1, -1, -1):
			s += "\nrestore a"+str(i)
		
		return s
		
class ThisExpression:

	def __init__(self, startLine, endLine):
		self.represents = "this"
		self.startLine = startLine
		self.endLine = endLine
		self.type = None
			
	def toString(self):
		s = "This"
		return s
		
	def getType(self, containingClass):
		self.type = TypeRecord(containingClass.name)
		return self.type
		
	# The 'this' expression represents the address of the object
	# record on the heap 
	# that represents an instance of the class that
	# the 'this' expression is found in
	# Since we assume that 'this' is always stored in
	# register a0 we can set the result register to a0
	# and return an empty string since there is no AMI code
	# implicitly associated with evaluating a 'this' expression
	def getAMI(self, containingClass, declaration, breakLabel, continueLabel):
		self.resultReg = "a0"
		return ""
		
class SuperExpression:

	def __init__(self, startLine, endLine):
		self.represents = "super"
		self.startLine = startLine
		self.endLine = endLine
			
	def toString(self):
		s = "Super"
		return s
		
	def getType(self, containingClass):
		if (containingClass.superName is None):
			print "ERROR - No superclass found. Line "+str(self.startLine)+"."
			return TypeRecord("ERROR")
		else:
			return TypeRecord(containingClass.superName) 

# unused expression :(
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