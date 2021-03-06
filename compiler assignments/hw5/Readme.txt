README.txt:	this file

decaflexer.py	PLY/lex specification of Decaf tokens.
		Also defines "errorflag" used to signal error during
 		scanning/parsing.

decafparser.py	PLY/yacc specification of Decaf grammar.
		The encoded grammar rules appear in the same order as in
 		decaf manual.
		Defines "from_file" function that takes a file name and
 		parses that file's contents.
		"from_file" returns True if no error, and False if error.

decafc.py	Driver: processes arguments and gets file name to pass to 		decafparser.from_file
		Decaf programs are assumed to be in files with ".decaf"
		suffix.
		Argument given to decafch may omit this suffix; e.g.
				python decafch test
		will read from test.decaf.

ast.py		Defines table and class definitions for Decaf's AST.
		Includes code to perform type-checking on the AST after
		construction.
		Includes code generation to produce Abstract Machine 
		Instructions as an intermediate form of the source code.