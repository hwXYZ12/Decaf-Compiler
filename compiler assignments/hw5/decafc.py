""" Decaf compiler
A compiler for Decaf programs
Usage: python decafc.py <filename>
where <filename> is the name of the file containing the Decaf program.
"""
import sys
import getopt
from decafparser import classes
from ast import DecafClass

import decafparser

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
        
    # parse command line options
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise Usage(msg)
        for o,a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0
        if (len(args) != 1):
            raise Usage("A single file name argument is required")
        fullfilename = args[0]
        if (fullfilename.endswith('.decaf')):
            (filename,s,e) = fullfilename.rpartition('.')
        else:
            filename=fullfilename
        infile = filename + ".decaf"
        if decafparser.from_file(infile):
			print "No syntax errors found."
			# after parsing using the attribute grammar
			# and producing the AST we perform type checking
			# Note that we need a completed AST in order to properly
			# perform type checking so this compilation phase
			# is distinct
			for c in classes:
				c.typeCheck()

			# TODO debug code
			# print each class from the generated list of decaf classes
			#for c in classes:
			#	c.printClass()
			
			# open a file to write the AMI instructions to
			newFileName = filename + ".ami"
			amiFile = open(newFileName, 'w')
				
			# write the AMI for each class to the
			# ami output file
			for c in classes:
				amiFile.write(c.getAMI())
				
			# write a single line static directive
			amiFile.write(".static_data "+str(DecafClass.totalStaticFields))
			
			amiFile.close()
			
        else:
            print "Failure: there were errors."
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "For help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
