This folder contains a copy of the PLY source files that can be found at http://www.dabeaz.com/ply/
More importantly, though, are 3 python files intended to scan and parse an input file to determine whether it is a grammatically and syntactically valid decaf program or not:

decaflexer.py - Token specification of a PLY/lex scanner that will tokenize decaf programs. The specification is based on the decaf manual.

decafparser.py - Grammar specification of a PLY/yacc parser that will use the tokens from the decaflexer.py program and determine whether or not the input represents a grammatically valid decaf program. As alluded to above, this grammar specification will also be based on the decaf manual. Neither parsetab.py nor parser.out will be included in the homework repo as PLY/yacc will regenerate both files. Fortunately, I was able to put together a grammar specification that was conflict-free (homework outline requires that any conflicts are described in the README).

decafch.py - The "main" program that utilizes decaflexer.py and decafparser.py to determine whether a given text file represents a syntactically and grammatically valid decaf program. The input is a single file path and the output is either a "success" message or the first line that an error occurs on. Both decaflexer.py and decafparser.py utilize PLY to generate the necessary scanner and parser tables, respectively.



**This is a CSE 304 submission (as opposed to a CSE 504 submission) and so program execution will adhere to the following exceptions...

(copied from the course website)
'CSE 304 students are expected to build a syntax checker for the following subset of Decaf:
Simple string constants. String constants may themselves not contain the delimiting " character. Thus, a string constant begins a " and ends with a " with no " in between.
Simple floating point constants. Floating point constants will be only of the first kind (page 2 of the manual): a decimal point `.' with a sequence of one or more digits on either side of it. That is, floating point constants will not use the exponent notation.
No arrays! This subset will not support the declaration of array-valued fields and variables (page 3 of the manual), array expressions (array_access in page 6), and array creation (new_array in page 7).
Moreover, their syntax checkers are expected to identify only the first syntax error in a program.'