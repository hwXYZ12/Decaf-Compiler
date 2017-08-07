# Decaf-Compiler
A compiler written in Python that takes a subset of Java as input (dubbed Decaf, which uses the .decaf extension) and converts it to Abstract Machine Instructions (which uses the .ami extension). The PLY Python lexer/parser is included with it's copyright as this compiler relies on PLY heavily. You can find PLY here
http://www.dabeaz.com/ply/

The file structure will reveal that this was a University project as there were a number of homework assignments
representing the incremental steps involved.

The key files of the final product are found in the hw5 folder and are the ast.py, decafc.py, decafparser.py, decaflexer.py files. They each represent the abstract syntax tree, the command line entry point to the program, the parser, and the lexer respectively.