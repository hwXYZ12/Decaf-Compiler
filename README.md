# Decaf-Compiler
A compiler written in Python that takes a subset of Java as input (dubbed Decaf, which uses the .decaf extension) and converts it to Abstract Machine Instructions (which uses the .ami extension). The PLY Python lexer/parser is included with it's copyright as this compiler relies on PLY heavily. You can find PLY here
http://www.dabeaz.com/ply/

The file structure will reveal that this was a University project as there were a number of homework assignments
representing the incremental steps involved.

The key files of the final product are found in the hw5 folder and are the ast.py, decafc.py, decafparser.py, decaflexer.py files. They each represent the abstract syntax tree, the command line entry point to the program, the parser, and the lexer respectively.



*There is a small note that should be made clear. This course was taken as the undergraduate version (as opposed to the graduate level version) which did not require converting the abstract machine instructions into actual machine instructions hence you cannot actually run a program compiled by this project. In some sense that means the compiler is incomplete but realistically one would want to use a state of the art compiler for his/her project (for obvious reasons, one of them being that the myriad optimizations that are present in modern compilers are unashamedly absent in this project).