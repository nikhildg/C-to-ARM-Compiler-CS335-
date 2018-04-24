#!/usr/bin/python
import ply.lex as lex
import sys

# LIST OF RESERVED KEYWORDS IN C# http://www.dotnetfunda.com/codes/show/945/list-of-csharp-reserved-keyword
# Contextual keywords not included in this list as they are used to provide a specific meaning in the code, but are not a reserved word in C#.
reserved_keywords = [
	'ABSTRACT', 'AS', 'BASE', 'BOOL', 'BREAK', 'BYTE', 
	'CASE', 'CATCH', 'CHAR', 'CHECKED', 'CLASS', 'CONST', 'CONTINUE', 
	'DECIMAL', 'DEFAULT', 'DELEGATE', 'DO', 'DOUBLE', 'ELSE', 'ENUM', 
	'EVENT', 'EXPLICIT', 'EXTERN', 'FALSE', 'FINALLY', 'FIXED', 'FLOAT', 
	'FOR', 'FOREACH', 'GOTO', 'IF', 'IMPLICIT', 'IN', 'INT', 
	'INTERFACE', 'INTERNAL', 'IS', 'LOCK', 'LONG', 'NAMESPACE', 
	'NEW', 'NULL', 'OBJECT', 'OPERATOR', 'OUT', 'OVERRIDE', 
	'PARAMS', 'PRIVATE', 'PROTECTED', 'PUBLIC', 'READONLY', 'REF', 
	'RETURN', 'SBYTE', 'SEALED', 'SHORT', 'SIZEOF', 'STACKALLOC', 'STATIC', 
	'STRING', 'STRUCT', 'SWITCH', 'THIS', 'THROW', 'TRUE', 'TRY', 'TYPEOF', 
	'UINT', 'ULONG', 'UNCHECKED', 'UNSAFE', 'USHORT', 'USING', 'VIRTUAL', 
	'VOID', 'VOLATILE', 'WHILE'
]

#LIST OF TOKENS
tokens = [
    # Integer literals
    'ICONST', 'UICONST','LICONST', 'ULICONST', 

	# Literals: Identifiers, Int-Constants, Char-Constant, String-Constant 
	'IDENTIFIER', 'CHCONST', 'STRCONST',

	# Primary Operators: . ?. ++ -- ->
	'MEMBERACCESS', 'CONDMEMBACCESS', 'INCREMENT', 'DECREMENT', 'ARROW',
	# Unary Operators: ~ ! 
	'NOT', 'LNOT',
	# Multiplicative Operators: * / %
	'TIMES', 'DIVIDE', 'MOD',
	# Additive Operators + -
	'PLUS', 'MINUS',
	# Shift Operators: << >>
	'LSHIFT', 'RSHIFT',
	# Relational Operators: < > <= >=
	'LT', 'GT', 'LE', 'GE',
	# Equality Operators == !=
	'EQ', 'NE',
	# Logical Operators: & ^ | && ||
	'AND', 'XOR', 'OR', 'CAND', 'COR',
	# Conditional Operator: ?
	'CONDOP',
	# Assignment and Lambda Operators: = += -= *= /= %= &= |= ^= <<= >>= =>
	'EQUALS', 'PLUSEQUAL', 'MINUSEQUAL', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL',
	'ANDEQUAL', 'OREQUAL', 'XOREQUAL', 'LSHIFTEQUAL', 'RSHIFTEQUAL',
	'LAMBDADEC',

	# Delimiters: ( ) { } [ ] , . ; :
	'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET', 'COMMA', 'PERIOD', 'STMT_TERMINATOR', 'COLON',
	# Others: \n // ...
	'NEWLINE', 'COMMENT', 'ELLIPSIS', 'PREPROCESSOR'

] + reserved_keywords

reserved = {}
for i in reserved_keywords:
    reserved[i.lower()] = i

# ignored charactes (space tab form feed)
t_ignore = ' \t\x0c'


# Operators
t_MEMBERACCESS		= r'\.'
t_CONDMEMBACCESS	= r'\?\.'
t_INCREMENT			= r'\+\+'
t_DECREMENT			= r'--'
t_ARROW				= r'->'
t_NOT 				= r'~'
t_LNOT				= r'!'
t_TIMES				= r'\*'
t_DIVIDE 			= r'/'
t_MOD   			= r'%'
t_PLUS  			= r'\+'
t_MINUS 			= r'-'
t_LSHIFT 			= r'<<'
t_RSHIFT 			= r'>>'
t_LT				= r'<'
t_GT				= r'>'
t_LE 				= r'<='
t_GE  				= r'>='
t_EQ   				= r'=='
t_NE   				= r'!='
t_AND  				= r'&'
t_XOR   			= r'\^'
t_OR     			= r'\|'
t_CAND  			= r'&&'
t_COR    			= r'\|\|'
t_CONDOP  			= r'\?'
t_EQUALS     		= r'='
t_PLUSEQUAL   		= r'\+='
t_MINUSEQUAL  		= r'-='
t_TIMESEQUAL 		= r'\*='
t_DIVEQUAL  		= r'/='
t_MODEQUAL 			= r'%='
t_ANDEQUAL   		= r'&='
t_OREQUAL    		= r'\|='
t_XOREQUAL    		= r'\^='
t_LSHIFTEQUAL  		= r'<<='
t_RSHIFTEQUAL  		= r'>>='
t_LAMBDADEC  		= r'=>'

# Delimiters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACKET         = r'\['
t_RBRACKET         = r'\]'
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
t_PERIOD           = r'\.'
t_STMT_TERMINATOR  = r';'
t_COLON            = r':'
t_ELLIPSIS         = r'\.\.\.'

# Identifiers and Keywords
def t_IDENTIFIER(t):
    r'[a-zA-Z_@][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'IDENTIFIER')    #  Check for reserved words
    return t

# newline
def t_NEWLINE(t):
	r'\n+'
	t.lexer.lineno += len(t.value)

#Literal definations

# Integer Literals
decimal_literal = r'-\d+|\d+'
hex_literal = r'0[Xx][0-9a-fA-F]+'
t_ULICONST = hex_literal + r'|' + decimal_literal + r'[uU][lL]|[lL][uU]'
t_UICONST = hex_literal + r'|' + decimal_literal + r'[Uu]'
t_LICONST = hex_literal + r'|' + decimal_literal + r'[Ll]'
t_ICONST = hex_literal + r'|' + decimal_literal

# String literal
t_STRCONST = r'\"([^\\\n]|(\\.))*?\"'

# Character constant 'c' or L'c'
t_CHCONST = r'(L)?\'([^\\\n]|(\\.))*?\''

# Comments
t_COMMENT = r'/\*(.|\n)*?\*/' + r'|' + r'//(.)*'

# Preprocessor directive (ignored)
def t_PREPROCESSOR(t):
    r'\#(.)*?\n'
    t.lineno += 1

# Error handling rule
def t_error(t):
    print(" Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Input filename from terminal
strinputfile = sys.argv[1]
inputfile = open(strinputfile, 'r')

#Convert file to string as lexer takes only string inputs.
data = inputfile.read()
lexer.input(data)
tokentype = {}   #dict to store token information
lexeme = {}      #dict to store lexeme for different token
non_recountable = ['IDENTIFIER']  #for token not to be recounted like variable names


while (1):
#processing token iteratively
    new_tok = lexer.token() #parse a new token
    if not new_tok:         #token is NULL
        break      
    else:
        tokname = new_tok.value         #store the lexeme
        toktype = new_tok.type          #stores the token_type
    if toktype not in tokentype:        #searching in dictionary tokentype
        tokentype[toktype] = 1          #initialize to 1
        lexeme[toktype]=[]              #initialize the list in the lexeme dictionary
        lexeme[toktype].append(tokname) #append lexeme to the lexeme dictionary
    else:
        if tokname not in lexeme[toktype]:
            lexeme[toktype].append(tokname)     #if not present add. above check avoids repetitions
            tokentype[toktype] += 1         #add another token seen of that type
        else:
            if toktype not in non_recountable:          #if this token type is not to be recounted
                tokentype[toktype] +=1          #add token seen.

#printing the tokens
for types in tokentype:
    print("*"*80)
    c = 0
    for lexlist in lexeme[types]:
        if c == 0 :
           print("{0:<20s} {1:>5s} {2:>40s}".format(types, (str)(tokentype[types]), lexlist))
           c = 1
        else:
           print("{0:>67s}".format(lexlist))
print("*"*80)

