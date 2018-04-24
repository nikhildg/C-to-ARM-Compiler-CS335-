#!/usr/bin/python
import ply.lex as lex
from ply.lex import TOKEN
import sys

# LIST OF RESERVED KEYWORDS IN C# http://www.dotnetfunda.com/codes/show/945/list-of-csharp-reserved-keyword
# Contextual keywords not included in this list as they are used to provide a specific meaning in the code, but are not a reserved word in C#.
reserved_keywords = [
	'ABSTRACT', 'AS', 'BASE', 'BOOL', 'BREAK', 'BYTE', 
	'CASE', 'CONSOLE', 'CATCH', 'CHAR', 'CHECKED', 'CLASS', 'CONST', 'CONTINUE', 
	'DECIMAL', 'DEFAULT', 'DELEGATE', 'DO', 'DOUBLE', 'ELSE', 'ENUM', 
	'EVENT', 'EXPLICIT', 'EXTERN', 'FALSE', 'FINALLY', 'FIXED', 'FLOAT', 
	'FOR', 'FOREACH', 'GOTO', 'IF', 'IMPLICIT', 'IN', 'INT', 
	'INTERFACE', 'INTERNAL', 'IS', 'LOCK', 'LONG', 'NAMESPACE', 
	'NEW', 'NULL', 'OBJECT', 'OPERATOR', 'OUT', 'OVERRIDE', 
	'PARAMS', 'PRIVATE', 'PROTECTED', 'PUBLIC', 'READONLY', 'REF', 
	'RETURN', 'SBYTE', 'SEALED', 'SHORT', 'SIZEOF', 'STACKALLOC', 'STATIC', 
	'STRING', 'STRUCT', 'SWITCH', 'THIS', 'THROW', 'TRUE', 'TRY', 'TYPEOF', 
	'UINT', 'ULONG', 'UNCHECKED', 'UNSAFE', 'USHORT', 'USING', 'VIRTUAL', 
	'VOID', 'VOLATILE', 'WHILE','READLINE', 'WRITELINE'
]

#LIST OF TOKENS
tokens = [
    # Integer literals
    'ICONST', 
    #'UICONST','LICONST', 'ULICONST', 
    #Real Literals
    'FCONST',

	# Literals: Identifiers, Int-Constants, Char-Constant, String-Constant 
	'IDENTIFIER', 
    'CHCONST', 
    'STRCONST',

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
	'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET', 'COMMA',  'STMT_TERMINATOR', 'COLON',
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
decimal_literal = r'\d+'
hex_literal = r'0[Xx][0-9a-fA-F]+'
#t_ULICONST = hex_literal + r'|' + decimal_literal + r'[uU][lL]|[lL][uU]'
#t_UICONST = hex_literal + r'|' + decimal_literal + r'[Uu]'
#t_LICONST = hex_literal + r'|' + decimal_literal + r'[Ll]'
t_ICONST = hex_literal + r'|' + decimal_literal

#Real Literals
type1 = r'\d*'+ r'\.'+r'([0-9]+)'+r'([eE][+-]?\d+)'+r'?'+r'([fFdDmM])'+r'?'
type2 =   r'([0-9]+)'+r'([fFdDmM])'  + r'([fFdDmM])' + r'?'
type3 = r'([0-9]+)' + r'([fFdDmM])'
fconst = type1 + r'|' + type2 + r'|' + type3
@TOKEN(fconst)
def t_FCONST(t):
    if t.value[-1].lower() == 'd':
        t.type = 'FCONST'
    else:
        t.type = 'FCONST'
    return t

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
