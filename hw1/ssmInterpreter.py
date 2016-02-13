import sys
import re
import pdb

# uses a regular expression to ensure that a label follows the correct form
def isLabel(str, regex=re.compile(r'[^0-9a-z_]')):
	return not bool(regex.search(str))
		
# uses a regular expression to determine whether a string is a positive integer or not
def isInteger(str, regex=re.compile(r'[^0-9]')):
	return not bool(regex.search(str))

print "Please enter SSM instructions to interpret. Terminate input with Ctrl-Z on Windows and Ctrl-D on Unix: "

# As stated in the problem specification "If an input program has errors (...), the interpreter should give an error message and exit *without executing a single instruction*"
# This implies that the program to be interpreted must pass a scanning phase before interpretation occurs.

input = sys.stdin.readlines()

# At this point we scan the input for errors.
# The input rules are as follows...
# An SSM program is a sequence of instructions.
# Each instruction may be preceded by an optional label and a semi-colon (":").
# A label is a sequence of alphabetic characters or numeric characters or underscore ("_"), beginning with an alphabetic character.
# An integer *num* is a sequence of numeric characters, optionally preceded by a minues ("-").
# The instructions in the assembly language should always be in lower-case.
# The instructions ildc, jz, jnz, and jmp take one argument; the other instructions have no arguments.
# The label may be separated from the following instruction by a sequence of zero or more whitespace (blank, tab, newline) characters.
# An instruction and its argument will be separated by a sequence of one or more whitespace characters.
# There may be more than one instruction in a line; or a single instruction may be split over multiple lines.
# The input assembly program may also have comments. A comment begins with "#" symbol and ends at the end of the line.

# Each instruction and each argument is separated by some form of whitespace, so we can use
# whitespace as a delimiter to get each instruction and its respective argument
# In order to incorporate labels and comments, the scan becomes a bit more involved
# How are labels incorporated?
# When we aren't checking for arguments then we are looking for labels and
# so we need only plant the code for that check in that branch
# How are comments incorporated? A comment essentially truncates a line
# before it is even processed, so that is what we will do line-by-line 

lineCount = 0
expectingIntArgument = False
expectingLabelArgument = False
instructions = []
instructionArguments = []
labels = {}
definedLabels = set()
usedJumps = set()
for line in input:

	# we have no need for any initial whitespace in 'line'
	line = line.lstrip()
	
	# skip any lines that are nothing but whitespace
	if(line == ""):
		continue
		
	# before we even consider processing a new line, we truncate it based off of the
	# first comment symbol found
	comment = line.find('#')
	if(comment >= 0):
		# we found a comment!
		# now truncate the rest of the string
		line = line[:comment] + '\n' # don't delete the newline character though... it's used in our algorithm		

	while True:
		whitespace1 = line.find(' ')
		whitespace2 = line.find('\t')
		whitespace3 = line.find('\n') # this character is guaranteed to be somewhere in the input
		
		# we have 3 possiblilites for the index of the next whitespace character
		# we either found or didn't find the ' ' and '\t' characters and we know that we
		# will always find a '\n' character. Thus there are 4 possible cases.
		if whitespace1 >= 0 and whitespace2 >= 0:
			whitespace = min(min(whitespace1, whitespace2), whitespace3)
		elif(whitespace1 == -1 and whitespace2 >= 0):
			whitespace = min(whitespace2, whitespace3)
		elif(whitespace1 >=0 and whitespace2 == -1):
			whitespace = min(whitespace1, whitespace3)
		else:
			whitespace = whitespace3
						
		if expectingLabelArgument or expectingIntArgument:
			# this is the branch we use if the last instruction we scanned requires an argument		
			argument = line[:whitespace]
			if expectingLabelArgument:
				# we just need to check that the label is properly formed AND we will need to check at some point that
				# the referenced label exists
				# we use a regular expression to check that the label is properly formed
				firstCharacter = argument[0]				
				if not (str(firstCharacter).isalpha() and str(firstCharacter).islower()):
					# the first character in the label ISN'T a lower case alphabetical symbol, we terminate with a
					# scanner error
					print "ERROR - Line " + str(lineCount) + " - Improperly Formed Label"
					sys.exit()
				elif not isLabel(argument):
					# we also check the other characters in the string using a regular expression							
					print "ERROR - Line " + str(lineCount) + " - Improperly Formed Label"
					sys.exit()
				else:				
					# this is the case that the label IS properly formed
					instructionArguments.append(argument)
					expectingLabelArgument = False
					
					# keep track of this label as we will need to double-check
					# after all of the input has been scanned that this label has been defined
					usedJumps.add(argument)
					
					# we also need to update the 'line' variable to reflect
					# that we've processed a label					
					line = line[whitespace:]
					line = line.lstrip()
							
			elif expectingIntArgument:
				# we just check that the argument is an integer
				# we use another regular expression to achieve this
				firstCharacter = argument[0]				
				if (firstCharacter == '-'):
					# the first character is negative
					# so we splice the string and check it without the first character
					if(isInteger(argument[1:])):
						# this means that the integer is correctly formed and we add it to our list
						# of arguments
						instructionArguments.append(argument)
						expectingIntArgument = False
					else:
						# otherwise we have an error and quit the program
						print "ERROR - Line " + str(lineCount) + " - Expected an Integer"
						sys.exit()
				elif(isInteger(argument)):
						# this means that the integer is correctly formed and we add it to our list
						# of arguments
						instructionArguments.append(argument)
						expectingIntArgument = False
					
						# we also need to update the 'line' variable to reflect
						# that we've processed a label					
						line = line[whitespace:]
						line = line.lstrip()
				else:
					# otherwise we have an error and quit the program
					print "ERROR - Line " + str(lineCount) + " - Expected an Integer"
					sys.exit()								
		else:	
		
			# we've handled the case that we're looking for an argument so
			# we must at this point be looking for either an instruction or a label
			colon = line.find(':')
			if(colon >= 0):
				# we have discovered a colon and must be dealing with a label
				# since we are at the start of either an instruction or a label
				# we need only check that there is either nothing or only whitespace between the label 
				# and the discovered colon (if there is anything else, then we assume that
				# there is an instruction between the label and the start of the line)
				label = line[:colon]
				inBetween = line[whitespace:colon]
				if (inBetween == "" or inBetween.isspace()):
					# we've found a new label and can process it
					
					# ensure that the label follows the correct format
					firstCharacter = label[0]				
					if not (str(firstCharacter).isalpha() and str(firstCharacter).islower()):
						# the first character in the label ISN'T a lower case alphabetical symbol, we terminate with a
						# scanner error
						print "ERROR - Line " + str(lineCount) + " - Improperly Formed Label"
						sys.exit()
					elif not isLabel(label):
						# we also check the other characters in the string using a regular expression							
						print "ERROR - Line " + str(lineCount) + " - Improperly Formed Label"
						sys.exit()
						
					# we also need to update the 'line' variable to reflect
					# that we've processed a label					
					# shift the 'line' to the one position past the colon
					line = line[(colon+1):]		
					
					# and delete any whitespace that may be left over
					line = line.lstrip()
					
					# add the label to our dictionary of labels
					labels[label] = lineCount
					
					# add the label to the set of defined labels
					definedLabels.add(label)
					
					# note that after we've processed the label, we may need to break to the next line
					if(line == "" or line == "\n"):
						break	# breaks the 'while True' loop
						
					continue	# ensures that we don't do any unnecessary processing in this loop
				#else:
					# we've discovered that we're NOT dealing with a label, in fact the label
					# must be further down the line and there is at least one instruction preceding
					# it. Thus we continue processing as if we expect an instruction
						
			# now that we know the next whitespace character index, we can use
			# it to substring the input and determine the instruction that we're interested in
			inst = line[:whitespace]
			
			# substring the line in order to remove the instruction AND strip the following whitespace 
			line = line[whitespace:]
			line = line.lstrip()
			
			# now that we have the instruction, we must determine which instruction it is
			# and proceed from there
			if(inst == "isub" or inst == "iadd" or inst == "imul" or inst == "idiv" or inst == "imod" or inst == "pop" or inst == "dup" or inst == "swap" or inst == "load" or inst == "store"):
				# any of these instructions don't require any extra arguments
				# we can just add the instruction to our list of instructions and move to the next instruction
				instructions.append(inst)
				instructionArguments.append("")
			elif(inst == "ildc"):
				# this single instruction requires an integer argument
				instructions.append(inst)
				expectingIntArgument = True;
				expectingLabelArgument = False;
			elif(inst == "jz" or inst == "jnz" or inst == "jmp"):
				# these instruction require exactly one label argument
				instructions.append(inst)
				expectingIntArgument = False;
				expectingLabelArgument = True;
			else:
				# if the instruction doesn't match any of the above strings, then we terminate and print an error
				print "Error - Line " + str(lineCount) + " - Invalid Instruction"
				sys.exit()
							
		# once we've checked the instruction or argument we check whether we ought to break to the next line
		if(line == "" or line == "\n"):
			break
	
	lineCount+= 1
	
# before the scan completes, we need to check that every jump corresponds to a label that
# has been defined	
if not (usedJumps.issubset(definedLabels)):
	print "A jump argument is used that has not been defined!"
	quit()
		
# I believe this scanner is approximately what we need. It's possible that I've overlooked or missed something but at this point
# I feel that it's time to write the portion of the code that actually interprets the code as opposed to merely scanning
# it for compilation errors
# How are we going to process the code? Well, as the problem specification is stated, we execute each instruction sequentially until the last instruction
# has executed and print the top-most value on the stack. In the case that the program attempts to access an empty stack the program should exit and an error message printed.
# In the case that the program attempts to access a value in a cell in store without initializing the cell first, the program should exit and an error printed.

# Fortunately, we stored some information during the scanning process that will make interpreting the program a bit more straightforward
theStack = []
theStore = {}
whichInstruction = 0
while(True):

	# end of program is reached, don't interpret anything else and print the top of the stack
	if(whichInstruction >= len(instructions)):
		if(len(theStack) < 1):
			print "The program terminated and the stack is empty!"
		else:
			print theStack.pop()
		break
				
	theInst = instructions[whichInstruction]
	
	# using a massive if-elif...elif construct to emulate a case / switch construct
	if(theInst == "iadd"):
		# pop the top two elements of the stack, add them, and push their sum on to the stack.
		
		# if the stack doesn't have two elements or more, we exit and print an error
		if(len(theStack) < 2):
			print "ERROR - Attempt to access an empty stack!"
			quit()
		
		x1 = int(theStack.pop())
		x2 = int(theStack.pop())
		
		theStack.append(x1+x2)
		
		# move instruction pointer forward
		whichInstruction+=1
	
	elif(theInst == "isub"):
		# subtract the top-most element on stack from the second-to-top element; pop the top two elements of the stack, and push the result of the subtraction on to the stack.
		
		# if the stack doesn't have two elements or more, we exit and print an error
		if(len(theStack) < 2):
			print "ERROR - Attempt to access an empty stack!"
			quit()
					
		x1 = int(theStack.pop())
		x2 = int(theStack.pop())
		
		theStack.append(x2-x1)
		
		# move instruction pointer forward
		whichInstruction+=1
		
	elif(theInst == "imul"):
		# pop the top two elements of the stack, multiply them, and push their product on to the stack.
		
		# if the stack doesn't have two elements or more, we exit and print an error
		if(len(theStack) < 2):
			print "ERROR - Attempt to access an empty stack!"
			quit()
					
		x1 = int(theStack.pop())
		x2 = int(theStack.pop())
		
		theStack.append(x2*x1)
		
		# move instruction pointer forward
		whichInstruction+=1
		
	elif(theInst == "idiv"):
		# divide the second-to-top element on the stack by the top-most element; pop the top two elements of the stack, and push the result of the division (the quotient) on to the stack.
		
		# if the stack doesn't have two elements or more, we exit and print an error
		if(len(theStack) < 2):
			print "ERROR - Attempt to access an empty stack!"
			quit()
						
		x1 = int(theStack.pop())
		x2 = int(theStack.pop())
		
		theStack.append(x2 // x1)
		
		# move instruction pointer forward
		whichInstruction+=1
		
	elif(theInst == "imod"):
		# divide the second-to-top element on the stack by the top-most element; pop the top two elements of the stack, and push the result of the division (the remainder) on to the stack.
		
		# if the stack doesn't have two elements or more, we exit and print an error
		if(len(theStack) < 2):
			print "ERROR - Attempt to access an empty stack!"
			quit()
									
		x1 = int(theStack.pop())
		x2 = int(theStack.pop())
		
		theStack.append(x2 % x1)
		
		# move instruction pointer forward
		whichInstruction+=1
		
	elif(theInst == "pop"):
		# pop the top-most element of the stack.
				
		# if the stack doesn't have one element or more, we exit and print an error
		if(len(theStack) < 1):
			print "ERROR - Attempt to access an empty stack!"
			quit()
			
		theStack.pop()
				
		# move instruction pointer forward
		whichInstruction+=1
		
	elif(theInst == "dup"):
		#  push the value on the top of stack on to the stack (i.e. duplicate the top-most entry in the stack).
				
		# if the stack doesn't have one element or more, we exit and print an error
		if(len(theStack) < 1):
			print "ERROR - Attempt to access an empty stack!"
			quit()
			
		x1 = int(theStack.pop())
		theStack.append(x1)
		theStack.append(x1)
		
		# move instruction pointer forward
		whichInstruction+=1
		
	elif(theInst == "swap"):
		#  swap the top two values on the stack. That is, if n is the top-most value on the stack, and m is immediately below it, make m the top most value of the stack with n immediately below it.
				
		# if the stack doesn't have at least 2 elements or more, we exit and print an error
		if(len(theStack) < 2):
			print "ERROR - Attempt to access an empty stack!"
			quit()
									
		x1 = int(theStack.pop())
		x2 = int(theStack.pop())
		theStack.append(x1)
		theStack.append(x2)
		
		# move instruction pointer forward
		whichInstruction+=1
		
	elif(theInst == "load"):
		# the top-most element of the stack is the address in store, say a. This instruction pops the top-most element, and takes the value at address a in store, and pushes that value to the stack.
		
		# if the stack doesn't have one element or more, we exit and print an error
		if(len(theStack) < 1):
			print "ERROR - Attempt to access an empty stack!"
			quit()
			
		x1 = int(theStack.pop())
	
		# if we've attempted to access a cell in the storage that hasn't
		# been initialized, we let the user know that an error has occurred
		if not (x1 in theStore):
			print "ERROR - An attempt to acces an unitialized cell in the store has occurred!"
			quit()
		
		theStack.append(theStore[x1])
		
		# move instruction pointer forward
		whichInstruction+=1		
		
	elif(theInst == "store"):
		# treat the second-to-top element on the stack as an address a, and the top-most element as an integer i. Pop the top two elements from stack. The cell at address a in the store is updated with integer i.
		
		# if the stack doesn't have at least 2 elements or more, we exit and print an error
		if(len(theStack) < 2):
			print "ERROR - Attempt to access an empty stack!"
			quit()
									
		x1 = int(theStack.pop())
		x2 = int(theStack.pop())
		theStore[x2] = x1
		
		# move instruction pointer forward
		whichInstruction+=1		
			
	elif(theInst == "jz"):
		# pop the top most value from the stack; if it is zero, jump to the instruction labelled with the given label; otherwise go to the next instruction.
		
		# if the stack doesn't have one element or more, we exit and print an error
		if(len(theStack) < 1):
			print "ERROR - Attempt to access an empty stack!"
			quit()
			
		x1 = int(theStack.pop())
		if(x1 == 0):
			whichInstruction = labels[instructionArguments[whichInstruction]]
		else:
			whichInstruction += 1
			
	elif(theInst == "jnz"):
		#  pop the top most value from the stack; if it is not zero, jump to the instruction labelled with the given label; otherwise go to the next instruction.
		
		# if the stack doesn't have one element or more, we exit and print an error
		if(len(theStack) < 1):
			print "ERROR - Attempt to access an empty stack!"
			quit()
			
		x1 = int(theStack.pop())
		if(x1 != 0):
			whichInstruction = labels[instructionArguments[whichInstruction]]
		else:
			whichInstruction += 1
			
	elif(theInst == "jmp"):
		# jump to the instruction labelled with the given label.		
		whichInstruction = labels[instructionArguments[whichInstruction]]
		
	elif(theInst == "ildc"):
		# push the given integer num on to the stack.
		theStack.append(int(instructionArguments[whichInstruction]))
		
		# move instruction pointer forward
		whichInstruction+=1
		
		