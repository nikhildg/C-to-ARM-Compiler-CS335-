#!/usr/bin/python3
#http://www.cs.may.ie/~jpower/Research/csharp/csharp.y
###################################################################################################

import sys
import ply.yacc as yacc
from lexer import *
from sym_table import *
import copy

filename = sys.argv[1]
symbol_table = env()

#precedence
precedence = (
    ('left', 'COR'),
    ('left', 'CAND'),
    ('left', 'OR'),
    ('left', 'XOR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'GT', 'GE', 'LT', 'LE'),
    ('left', 'RSHIFT', 'LSHIFT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'NOT', 'LNOT'),
)


# Literal
def p_literal(p):
    """literal : boolean_literal
        | ICONST
        | FCONST
        | STRCONST
        | CHCONST
        | NULL
    """
    p[0] = {}
    p[0]['code'] = [""]
    p[0]['value'] = p[1]
    p[0]['uppertype'] = 'literal'

def p_boolean_literal(p):
    """ boolean_literal : TRUE
        | FALSE
    """

#### Syntactic grammar ####

# Basic concepts 
def p_namespace_name(p):
    """namespace_name : qualified_identifier
    """
def p_type_name(p):
    """type_name : qualified_identifier
    """

# Types 
def p_type(p):
    """type : non_array_type
        | array_type
    """
    p[0] = p[1]

def p_non_array_type(p):
    """non_array_type : simple_type
        | type_name
    """
    p[0] = p[1]

def p_simple_type(p):
    """simple_type : primitive_type
        | class_type
        | pointer_type
    """
    p[0] = p[1]

def p_primitive_type(p):
    """primitive_type : numeric_type
        | BOOL
        | VOID
    """
    if p[1]=='bool':
        p[0] = {'type':"bool",'uppertype':"basic",'width':1}
    elif p[1]=='void':
        p[0] = {'type':"void",'uppertype':"basic",'width':1}
    else:
        p[0]=p[1]

def p_numeric_type(p):
    """numeric_type : integral_type
        | floating_point_type
    """
    p[0] = p[1]

def p_integral_type(p):
    """integral_type : INT 
        | CHAR
    """
    if p[1] == 'int':
        p[0] = {'type':"int",'uppertype':"basic",'width':4}
    else:
        p[0] = {'type':"char",'uppertype':"basic",'width':1}

def p_floating_point_type(p):
    """floating_point_type : FLOAT 
        | DOUBLE
    """
    if p[1] == 'float':
        p[0] = {'type':"float",'uppertype':"basic",'width':4}
    else:
        p[0] = {'type':"double",'uppertype':"basic",'width':8}

def p_class_type(p):
    """class_type : OBJECT 
        | STRING
        | IDENTIFIER
    """
    if p[1] == 'string':
        p[0] = {'type':"string",'uppertype':"basic",'width':4}
    elif p[1] == 'IDENTIFIER':
        p[0] = {}
        p[0]['type']=p[1]
        p[0]['uppertype']='class'
    else:
        p[0] = {'type':"None",'uppertype':"object",'width':8}
    
def p_pointer_type(p):
    """pointer_type : type TIMES
        | VOID TIMES
    """

def p_dereferencer(p):
    """dereferencer : TIMES
    """

def p_array_type(p):
    """array_type : array_type rank_specifier
        | simple_type rank_specifier
        | qualified_identifier rank_specifier
    """
    p[0] = {'type':p[1]['type'],'uppertype':"array",'width':p[1]['width']}

def p_rank_specifiers_opt(p):
    """ rank_specifiers_opt : empty
        | rank_specifier rank_specifiers_opt
    """
def p_rank_specifier(p):
    """rank_specifier : LBRACKET RBRACKET
        | LBRACKET comma_plus RBRACKET
    """
def p_comma_plus(p):
    """comma_plus : COMMA
                | comma_plus COMMA
    """

# Variables 
def p_variable_reference(p):
    """variable_reference : expression
    """

# Expressions 
def p_argument_list(p):
    """argument_list : argument
        | argument_list COMMA argument
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]

def p_argument(p):
    """argument : expression
    """
    p[0] = p[1]

def p_primary_expression(p):
    """primary_expression : parenthesized_expression
        | primary_expression_no_parenthesis
        | anonymous_method_expression
    """
    p[0] = p[1]

def p_primary_expression_no_parenthesis(p):
    """primary_expression_no_parenthesis : literal
        | array_creation_expression
        | member_access
        | invocation_expression
        | element_access
        | this_access
        | base_access
        | new_expression
        | typeof_expression
        | sizeof_expression
        | checked_expression
        | unchecked_expression
    """
    p[0] = p[1]

def p_parenthesized_expression(p):
    """parenthesized_expression : LPAREN expression RPAREN
    """
    p[0] = p[2]
    
def p_member_access(p):
    """member_access : primary_expression MEMBERACCESS IDENTIFIER
        | primitive_type MEMBERACCESS IDENTIFIER
        | class_type MEMBERACCESS IDENTIFIER
    """
def p_invocation_expression(p):
    """invocation_expression : qualified_identifier LPAREN argument_list_opt RPAREN
    """
    p[0] = {}
    func_name = symbol_table.lookup(p[1]['value'],symbol_table.curr_table)
    if func_name == None:
        print("ERROR L", p.lineno(1), "Function", p[1]['value'], "not defined as a function")
        print("Compilation Terminated")
        exit()          
    elif func_name['uppertype'] != "function":
        print("ERROR L", p.lineno(1), "Function", p[1]['value'], "not defined as a function")
        print("Compilation Terminated")
        exit()          
    else:
        t = symbol_table.maketemp(func_name['type'], symbol_table.curr_table)
        p[0]['value'] = t
        p[0]['code'] = []
        if p[3]!=None and len(p[3])>0:
            arg_count = len(p[3])
            if arg_count != func_name['arg_num']:
                print("ERROR L", p.lineno(1), "Function", p[1]['value'], "needs exactly", func_name['arg_num'], "parameters, given", len(p[3]))
                print("Compilation Terminated")
                exit()
            for arg in p[3]:
                var = symbol_table.lookup(arg['value'],symbol_table.curr_table)
                if 'uppertype' in arg:
                    if arg['uppertype'] == 'literal':
                        pass
                elif var == None or var['uppertype']=='function' :
                    print("ERROR L", ": ", arg['value'], " has not been declared as variable")
                    print("Compilation Terminated")
                    exit()
            for arg in p[3]:
                p[0]['code'] += arg['code']
            for arg in p[3]:
                p[0]['code'] += ['param, '+ arg['value']]
        p[0]['code'] += ["call, " + p[1]['value']]
                
def p_argument_list_opt(p):
    """argument_list_opt : empty 
        | argument_list
    """
    p[0] = p[1]

def p_element_access(p):
    """element_access : qualified_identifier LBRACKET expression_list RBRACKET
    """
    p[0] = {}
    p[0]['code'] = []    
    var = symbol_table.lookup(p[1]['value'], symbol_table.curr_table)
    if var==None:
        print("ERROR L", p.lineno(1), ": symbol", p[0], "used without declaration")
        print("Compilation Terminated")
        exit()
    else:
        if var['uppertype'] != "array":
            print("ERROR L", p.lineno(1), "Function", p[1]['value'], "not defined as an array")
            print("Compilation Terminated")
            exit()
        else:
            t = symbol_table.maketemp(var['type'], symbol_table.curr_table)
            t1 = symbol_table.maketemp('int', symbol_table.curr_table)
            t2 = symbol_table.maketemp('int', symbol_table.curr_table)
            p[0]['code'] += ["=, " + t1 + ", " + p[3]['value']]
            p[0]['code'] += ['*, ' + t2 + ', ' + t1 + ', ' + str(var['width'])]
            p[0]['code'] += ["array_element, " +  t + ", " + p[1]['value'] + ", " + t2]
            p[0]['value'] = t
            
def p_expression_list(p):
    """expression_list : expression
    """
    p[0] = p[1]

def p_this_access(p):
    """this_access : THIS
    """
def p_base_access(p):
    """base_access : BASE MEMBERACCESS IDENTIFIER
        | BASE LBRACKET expression_list RBRACKET
    """
def p_post_increment_expression(p):
    """post_increment_expression : postfix_expression INCREMENT
    """
    t = symbol_table.maketemp('int', symbol_table.curr_table)
    p[0] = deepcopy(p[1])
    p[0]['value'] = t
    p[0]['code'] += ["=, " + t + ", " + p[1]['value']]
    p[0]['code'] += ["+, " + p[1]['value'] + ", 1, " + p[1]['value']]

def p_post_decrement_expression(p):
    """post_decrement_expression : postfix_expression DECREMENT
    """
    t = symbol_table.maketemp('int', symbol_table.curr_table)
    p[0] = deepcopy(p[1])
    p[0]['value'] = t
    p[0]['code'] += ["=, " + t + ", " + p[1]['value']]
    p[0]['code'] += ["-, " + p[1]['value'] +", " + p[1]['value'] +", 1"]

def p_new_expression(p):
    """new_expression : object_creation_expression
    """
    p[0] = p[1]

def p_object_creation_expression(p):
    """object_creation_expression : NEW class_type LPAREN argument_list_opt RPAREN
    """
    p[0] = {}
    class_name = symbol_table.class_search(p[2]['type'])
    if class_name:
        t = symbol_table.maketemp('int',symbol_table.curr_table)
        p[0]=deepcopy(p[3])
        p[0]['value'] = t
        # p[0]['type']=class_name.name
        # p[0]['uppertype']='class'
        print(type(class_name.width))
        p[0]['code'] = ["=alloc, "+ t +", "+ class_name.width]

    else:
        print("ERROR: Class",p[2],"used without declaration")
        print("Compilation Terminated")
        exit()
    

def p_array_creation_expression(p):
    """array_creation_expression : NEW non_array_type LBRACKET expression_list RBRACKET array_initializer_opt
        | NEW array_type array_initializer
    """
def p_array_initializer_opt(p):
    """array_initializer_opt : empty 
        | array_initializer
    """
def p_typeof_expression(p):
    """typeof_expression : TYPEOF LPAREN type RPAREN
        | TYPEOF LPAREN VOID RPAREN
    """
def p_checked_expression(p):
    """checked_expression : CHECKED LPAREN expression RPAREN
    """
def p_unchecked_expression(p):
    """unchecked_expression : UNCHECKED LPAREN expression RPAREN
    """
def p_pointer_member_access(p):
    """pointer_member_access : postfix_expression ARROW IDENTIFIER
    """
def p_addressof_expression(p):
    """addressof_expression : AND unary_expression
    """
def p_sizeof_expression(p):
    """sizeof_expression : SIZEOF LPAREN type RPAREN
    """
def p_postfix_expression(p):
    """postfix_expression : primary_expression
        | qualified_identifier
        | post_increment_expression
        | post_decrement_expression
        | pointer_member_access
    """
    p[0]=p[1]

def p_unary_expression_not_plusminus(p):
    """unary_expression_not_plusminus : postfix_expression
        | LNOT unary_expression
        | NOT unary_expression
        | cast_expression
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = deepcopy(p[2])
        if p[1] == '!':
            p[0]['code'] += ["!, " + p[0]['value']]
        elif p[1] == '~':
            p[0]['code'] += ["~, " + p[0]['value']]

def p_pre_increment_expression(p):
    """pre_increment_expression : INCREMENT unary_expression
    """
    p[0] = p[2]
    p[0]['code'] += ["+, " + p[2]['value'] + ", " +  p[2]['value'] + ", 1"]

def p_pre_decrement_expression(p):
    """pre_decrement_expression : DECREMENT unary_expression
    """
    p[0] = p[2]
    p[0]['code'] += ["-, " + p[2]['value'] + ", " +  p[2]['value'] + ", 1"]

def p_unary_expression(p):
    """unary_expression : unary_expression_not_plusminus
        | PLUS unary_expression
        | MINUS unary_expression
        | TIMES unary_expression
        | pre_increment_expression
        | pre_decrement_expression
    """
    p[0] = {}
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = deepcopy(p[2])
        if p[1] == '-':
            p[0]['code'] += ["-, " + p[0]['value'] + ", 0, " + p[0]['value']]

def p_cast_expression(p):
    """cast_expression : LPAREN expression RPAREN unary_expression_not_plusminus
        | LPAREN multiplicative_expression TIMES RPAREN unary_expression 
        | LPAREN qualified_identifier rank_specifier type_quals_opt RPAREN unary_expression 
        | LPAREN primitive_type type_quals_opt RPAREN unary_expression
        | LPAREN class_type type_quals_opt RPAREN unary_expression
        | LPAREN VOID type_quals_opt RPAREN unary_expression
    """
def p_type_quals_opt(p):
    """type_quals_opt : empty 
        | type_quals
    """
def p_type_quals(p):
    """type_quals : type_qual
        | type_quals type_qual
    """
def p_type_qual (p):
    """type_qual  : rank_specifier 
        | dereferencer
    """

    
def p_multiplicative_expression(p):
    """multiplicative_expression : unary_expression
        | multiplicative_expression TIMES unary_expression  
        | multiplicative_expression DIVIDE unary_expression
        | multiplicative_expression MOD unary_expression
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    else:
        p[0],p[1],p[3] = math_ops(p[0],p[1],p[3],p[2])

def p_additive_expression(p):
    """additive_expression : multiplicative_expression
        | additive_expression PLUS multiplicative_expression
        | additive_expression MINUS multiplicative_expression
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    else:
        p[0],p[1],p[3] = math_ops(p[0],p[1],p[3],p[2])

def p_shift_expression(p):
    """shift_expression : additive_expression 
        | shift_expression LSHIFT additive_expression
        | shift_expression RSHIFT additive_expression
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    else:
        p[0],p[1],p[3] = math_ops(p[0],p[1],p[3],p[2])

def p_relational_expression(p):
    """relational_expression : shift_expression
        | relational_expression LT shift_expression
        | relational_expression GT shift_expression
        | relational_expression LE shift_expression
        | relational_expression GE shift_expression
        | relational_expression IS type
        | relational_expression AS type
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    else:
        p[0],p[1],p[3] = math_ops(p[0],p[1],p[3],p[2])

def p_equality_expression(p):
    """equality_expression : relational_expression
        | equality_expression EQ relational_expression
        | equality_expression NE relational_expression
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    else:
        p[0],p[1],p[3] = math_ops(p[0],p[1],p[3],p[2])

def p_and_expression(p):
    """and_expression : equality_expression
    | and_expression AND equality_expression
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    elif len(p) == 4:
        p[0] = {}
        # if p[1]['type'] == 'int':
        p[0]['type'] = 'int'
        p[0],p[1],p[3] = math_ops(p[0], p[1], p[3], p[2])
        # else:
        #     print("ERROR: Incorrect type in AND expression")
        #     print("Compilation Terminated")
        #     exit()
    #"""and_expression : equality_expression
    #"""
    #p[0] = deepcopy(p[1])

def p_exclusive_or_expression(p):
    """exclusive_or_expression : and_expression
    """
    p[0] = deepcopy(p[1])

def p_inclusive_or_expression(p):
    """inclusive_or_expression : exclusive_or_expression
    |         inclusive_or_expression OR exclusive_or_expression
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    elif len(p) == 4:
        p[0] = {}
        # if p[1]['type'] == 'int':
        p[0]['type'] = 'int'
        p[0],p[1],p[3] = math_ops(p[0], p[1], p[3], p[2])
        # else:
        #     print("ERROR: Incorrect type in AND expression")
        #     print("Compilation Terminated")
        #     exit()


def p_conditional_and_expression(p):
    """conditional_and_expression : inclusive_or_expression
        | conditional_and_expression CAND inclusive_or_expression
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    else:
        p[0],p[1],p[3] = math_ops(p[0],p[1],p[3],p[2])

def p_conditional_or_expression(p):
    """conditional_or_expression : conditional_and_expression
        | conditional_or_expression COR conditional_and_expression
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    else:
        p[0],p[1],p[3] = math_ops(p[0],p[1],p[3],p[2])

def p_conditional_expression(p):
    """conditional_expression : conditional_or_expression
        | conditional_or_expression CONDOP expression COLON expression
    """
    p[0] = deepcopy(p[1])

def p_assignment(p):
    """assignment : unary_expression assignment_operator expression
    """
    p[0]={}
    p[0]['value'] = p[1]['value']
    p[0]['code'] = []
    var = symbol_table.lookup(p[1]['value'], symbol_table.curr_table)
    if var!=None:
        p[0]['code'] += p[3]['code']
        p[0]['code'] += p[1]['code']
        p[0]['code'] += ["=, " + p[0]['value'] + ", " + p[3]['value']]
    else:
        print("ERROR: symbol", p[1]['value'], " used without declaration")
        print("Compilation Terminated")
        exit()

def p_assignment_operator(p):
    """assignment_operator : EQUALS 
    """
    p[0] = p[1]

def p_expression(p):
    """expression : conditional_expression
        | lambda_expression
        | assignment
    """
    p[0] = deepcopy(p[1])

def p_constant_expression(p):
    """constant_expression : expression
    """
    p[0] = deepcopy(p[1])

def p_boolean_expression(p):
    """boolean_expression : expression
    """
    p[0] = deepcopy(p[1])

# Statements 
def p_statement(p):
    """statement : labeled_statement
        | declaration_statement
        | embedded_statement
    """
    p[0] = deepcopy(p[1])

def p_embedded_statement(p):
    """embedded_statement : block
        | empty_statement
        | expression_statement
        | selection_statement
        | iteration_statement
        | jump_statement
        | try_statement
        | checked_statement
        | unchecked_statement
        | lock_statement
        | using_statement
        | unsafe_statement
        | fixed_statement
    """
    p[0] = deepcopy(p[1])

def p_block(p):
    """block : LBRACE begin_scope statement_list_opt RBRACE
    """
    p[0] = deepcopy(p[3])
    symbol_table.end_scope()

def p_begin_scope(p):
    """begin_scope : empty
    """
    p[0] = p[1]
    symbol_table.begin_scope()

def p_statement_list_opt(p):
    """statement_list_opt : empty 
        | statement_list
    """
    p[0] = deepcopy(p[1])

def p_statement_list(p):
    """statement_list : statement
        | statement_list statement
    """
    p[0] = deepcopy(p[1])
    if len(p) == 3:
        p[0]['code'] += p[2]['code']
        p[0]['value'] = None

def p_empty_statement(p):
    """empty_statement : STMT_TERMINATOR
    """
def p_labeled_statement(p):
    """labeled_statement : IDENTIFIER COLON statement
    """
def p_declaration_statement(p):
    """declaration_statement : local_variable_declaration STMT_TERMINATOR
        | local_constant_declaration STMT_TERMINATOR
    """
    p[0] = deepcopy(p[1])

#variable declaration
def p_local_variable_declaration(p):
    """local_variable_declaration : type variable_declarators
    """
    p[0] = {}
    p[0]['type'] = p[1]['type']
    p[0]['code'] =[]
    for variable in p[2]:
        if symbol_table.lookup_in_this(variable['value'])!=None:
            print("ERROR L", p.lineno(1), ": ", variable['value'], " has been declared before in this scope")
            print("Compilation Terminated")
            exit()
        else:
            if p[1]['uppertype']=="array":
                symbol_table.insert_array(p[0]['type'], variable['value'],p[1]['width'])
                if 'initializer' in variable:
                    p[0]['code'] += ["array, " + p[0]['type'] + ", " +str(len(variable['initializer'])) +  ", " + variable['value']]
                    count = 0
                    for item in variable['initializer']:
                        p[0]['code'] += item['code']
                        p[0]['code'] += ['=, ' + variable['value'] + ", " + str(count) + ", " + item['value']]
                        count = count + 1
                else:
                    p[0]['code'] += ["array, " + p[0]['type'] + ", None" + ", " + variable['value']]
            else:
                symbol_table.insert_variable(p[0]['type'], variable['value'])
                if 'initializer' in variable:
                    p[0]['code'] += variable['initializer']['code']
                    p[0]['code'] += ["=, " + variable['value'] + ", " + variable['initializer']['value']]
                else:
                    p[0]['code'] += [p[0]['type'] + ", " + variable['value']]
            

def p_variable_declarators(p):
    """variable_declarators : variable_declarator
        | variable_declarators COMMA variable_declarator
    """
    if len(p) == 2:
        p[0] = [deepcopy(p[1])]
    else:
        p[0] = deepcopy(p[1]) + [deepcopy(p[3])]

def p_variable_declarator(p):
    """variable_declarator : IDENTIFIER
        | IDENTIFIER EQUALS variable_initializer
    """
    p[0] = {}
    p[0]['value'] = p[1]
    if len(p)==4:
        p[0]['initializer'] = p[3]

def p_variable_initializer(p):
    """variable_initializer : expression
        | array_initializer
        | stackalloc_initializer
    """
    p[0] = deepcopy(p[1])

def p_stackalloc_initializer(p):
    """stackalloc_initializer : STACKALLOC type LBRACKET expression RBRACKET
    """ 
    
def p_local_constant_declaration(p):
    """local_constant_declaration : CONST type constant_declarators
    """
def p_constant_declarators(p):
    """constant_declarators : constant_declarator
        | constant_declarators COMMA constant_declarator
    """
def p_constant_declarator(p):
    """constant_declarator : IDENTIFIER EQUALS constant_expression
    """
def p_expression_statement(p):
    """expression_statement : statement_expression STMT_TERMINATOR
    """
    p[0] = deepcopy(p[1])

def p_statement_expression(p):
    """statement_expression : invocation_expression
        | object_creation_expression
        | assignment
        | post_increment_expression
        | post_decrement_expression
        | pre_increment_expression
        | pre_decrement_expression
    """
    p[0] = deepcopy(p[1])

def p_selection_statement(p):
    """selection_statement : if_statement
    """
    p[0] = deepcopy(p[1])

def p_if_statement(p):
    """if_statement : IF LPAREN boolean_expression RPAREN embedded_statement
        | IF LPAREN boolean_expression RPAREN embedded_statement ELSE embedded_statement
    """
    p[0] = {}
    p[0]['code'] = []
    if len(p)==8:
        p[0]['else'] = symbol_table.newlabel()
        p[0]['after'] = symbol_table.newlabel()
        p[0]['code'] += p[3]['code'] + ['ifgoto, '+'==, '+p[3]['value']+" , 0, "+ p[0]['else']] 
        if p[5]!=None and 'code' in p[5]:
            p[0]['code'] += p[5]['code']
        p[0]['code'] += ['goto, '+ p[0]['after']]
        p[0]['code'] += ['label, ' + p[0]['else']]
        if p[7]!=None and 'code' in p[7]:
            p[0]['code'] += p[7]['code']
        p[0]['code'] += ['label, ' + p[0]['after']]
    else:
        p[0]['after'] = symbol_table.newlabel()
        p[0]['code'] += p[3]['code'] + ['ifgoto, '+'==, '+p[3]['value']+" , 0, "+ p[0]['after']] 
        if p[5]!=None and 'code' in p[5]:
            p[0]['code'] += p[5]['code']
        p[0]['code'] += ['goto, '+ p[0]['after']]
        p[0]['code'] += ['label, ' + p[0]['after']]
        
def p_iteration_statement(p):
    """iteration_statement : while_statement
        | do_statement
        | for_statement
        | foreach_statement
    """
    p[0] = p[1]

def p_unsafe_statement(p):
    """unsafe_statement : UNSAFE block
    """
def p_while_statement(p):
    """while_statement : WHILE LPAREN boolean_expression RPAREN embedded_statement
    """
    p[0] = {}
    p[0]['code'] = []
    p[0]['begin'] = symbol_table.newlabel()
    p[0]['after'] = symbol_table.newlabel()
    p[0]['code'] += ['label, ' + p[0]['begin']]
    if p[3]!=None and 'code' in p[3]:
        p[0]['code'] += p[3]['code']
    p[0]['code'] += ['ifgoto, '+'==, '+p[3]['value']+" , 0, "+ p[0]['after']]
    if p[5]!=None and 'code' in p[5]:
        p[0]['code'] += p[5]['code']
    p[0]['code'] += ['goto, ' + p[0]['begin']]
    p[0]['code'] += ['label, ' + p[0]['after']]
    
def p_do_statement(p):
    """do_statement : DO embedded_statement WHILE LPAREN boolean_expression RPAREN STMT_TERMINATOR
    """

def p_for_statement(p):
    """for_statement : FOR LPAREN for_initializer_opt STMT_TERMINATOR for_condition_opt STMT_TERMINATOR for_iterator_opt RPAREN embedded_statement
    """
    p[0] = {}
    p[0]['code'] = []
    p[0]['begin'] = symbol_table.newlabel()
    p[0]['after'] = symbol_table.newlabel()
    if p[3]!=None and 'code' in p[3]:
        p[0]['code'] += p[3]['code']
    p[0]['code'] += ['label, ' + p[0]['begin']]
    if p[5]!=None and 'code' in p[5]:
        p[0]['code'] += p[5]['code']
    p[0]['code'] += ['ifgoto, '+'==, '+p[5]['value']+" , 0, "+ p[0]['after']]
    if p[9]!=None and 'code' in p[9]:
        p[0]['code'] += p[9]['code']
    if p[7]!=None and 'code' in p[7]:
        p[0]['code'] += p[7]['code']
    p[0]['code'] += ['goto, ' + p[0]['begin']]
    p[0]['code'] += ['label, ' + p[0]['after']]

def p_for_initializer_opt(p):
    """for_initializer_opt : empty 
        | for_initializer
    """
    p[0] = deepcopy(p[1])

def p_for_condition_opt(p):
    """for_condition_opt : empty 
        | for_condition
    """
    p[0] = deepcopy(p[1])

def p_for_iterator_opt(p):
    """for_iterator_opt : empty 
        | for_iterator
    """
    p[0] = deepcopy(p[1])

def p_for_initializer(p):
    """for_initializer : local_variable_declaration
        | statement_expression_list
    """
    p[0] = deepcopy(p[1])

def p_for_condition(p):
    """for_condition : boolean_expression
    """
    p[0] = deepcopy(p[1])

def p_for_iterator(p):
    """for_iterator : statement_expression_list
    """
    p[0] = deepcopy(p[1])

def p_statement_expression_list(p):
    """statement_expression_list : statement_expression
        | statement_expression_list COMMA statement_expression
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    else:
        p[0] = {}
        p[0]['code'] = p[1]['code']
        p[0]['code'] += p[3]['code']
        p[0]['value'] = None

def p_foreach_statement(p):
    """foreach_statement : FOREACH LPAREN type IDENTIFIER IN expression RPAREN embedded_statement
    """
def p_jump_statement(p):
    """jump_statement : break_statement
        | continue_statement
        | goto_statement
        | return_statement
        | throw_statement
    """
    p[0] = deepcopy(p[1])

def p_break_statement(p):
    """break_statement : BREAK STMT_TERMINATOR
    """
def p_continue_statement(p):
    """continue_statement : CONTINUE STMT_TERMINATOR
    """
def p_goto_statement(p):
    """goto_statement : GOTO IDENTIFIER STMT_TERMINATOR
        | GOTO CASE constant_expression STMT_TERMINATOR
        | GOTO DEFAULT STMT_TERMINATOR
    """
def p_return_statement(p):
    """return_statement : RETURN expression_opt STMT_TERMINATOR
    """
    p[0] = {}
    p[0]['code'] = []
    if p[2]!=None:
        if 'code' in p[2]:
            p[0]['code'] += p[2]['code']
            p[0]['code'] += ['return, ' + p[2]['value']]
    else:
        p[0]['code'] += ['return']

def p_expression_opt(p):
    """expression_opt : empty 
        | expression
    """
    p[0] = p[1]

def p_throw_statement(p):
    """throw_statement : THROW expression_opt STMT_TERMINATOR
    """
def p_try_statement(p):
    """try_statement : TRY block catch_clauses
        | TRY block finally_clause
        | TRY block catch_clauses finally_clause
    """
def p_catch_clauses(p):
    """catch_clauses : catch_clause
        | catch_clauses catch_clause
    """
def p_catch_clause(p):
    """catch_clause : CATCH LPAREN class_type identifier_opt RPAREN block
        | CATCH LPAREN type_name identifier_opt RPAREN block
        | CATCH block
    """
def p_identifier_opt(p):
    """identifier_opt : empty 
        | IDENTIFIER
    """
def p_finally_clause(p):
    """finally_clause : FINALLY block
    """
def p_checked_statement(p):
    """checked_statement : CHECKED block
    """
def p_unchecked_statement(p):
    """unchecked_statement : UNCHECKED block
    """
def p_lock_statement(p):
    """lock_statement : LOCK LPAREN expression RPAREN embedded_statement
    """
def p_using_statement(p):
    """using_statement : USING LPAREN resource_acquisition RPAREN embedded_statement
    """
def p_resource_acquisition(p):
    """resource_acquisition : local_variable_declaration
        | expression
    """
def p_fixed_statement(p):
    """fixed_statement : FIXED LPAREN type fixed_pointer_declarators RPAREN embedded_statement
    """
def p_fixed_pointer_declarators(p):
    """fixed_pointer_declarators : fixed_pointer_declarator
        | fixed_pointer_declarators COMMA fixed_pointer_declarator
    """
def p_fixed_pointer_declarator(p):
    """fixed_pointer_declarator : IDENTIFIER EQUALS expression
    """

# Lambda Expressions
def p_lambda_expression(p):
    """lambda_expression : explicit_anonymous_function_signature LAMBDADEC block
                        | explicit_anonymous_function_signature LAMBDADEC expression
    """

# Anonymous Method Expression
def p_anonymous_method_expression(p):
    """anonymous_method_expression : DELEGATE explicit_anonymous_function_signature_opt block
    """
def p_explicit_anonymous_function_signature_opt(p):
    """explicit_anonymous_function_signature_opt : explicit_anonymous_function_signature
                                                | empty
    """
def p_explicit_anonymous_function_signature(p):
    """explicit_anonymous_function_signature : LPAREN explicit_anonymous_function_parameter_list_opt RPAREN
    """
def p_explicit_anonymous_function_parameter_list_opt(p):
    """explicit_anonymous_function_parameter_list_opt : explicit_anonymous_function_parameter_list
                                                        | empty
    """
def p_explicit_anonymous_function_parameter_list(p):
    """explicit_anonymous_function_parameter_list : explicit_anonymous_function_parameter
                                                    | explicit_anonymous_function_parameter_list COMMA explicit_anonymous_function_parameter
    """
def p_explicit_anonymous_function_parameter(p):
    """explicit_anonymous_function_parameter : type IDENTIFIER
    """ 

# Compilation Unit
def p_compilation_unit(p):
    """compilation_unit : using_directives_opt
        | using_directives_opt namespace_member_declarations
    """
    if len(p)==2:
        p[0] = p[1]
    elif len(p)==3:
        p[0] = p[2]
    line_no = 1
    print (str(line_no) + ", call, Main")
    line_no = line_no + 1
    print (str(line_no) + ", exit") 
    for scope in p[0]:
        # print(scope)
        for line in scope['code']:
            # print(line)
            if line == "":
                continue
            line_no = line_no + 1
            print (str(line_no) + ", " + line)

def p_using_directives_opt(p):
    """using_directives_opt : empty 
        | using_directives
    """
def p_namespace_member_declarations_opt(p):
    """namespace_member_declarations_opt : empty 
        | namespace_member_declarations
    """
    p[0] = deepcopy(p[1])

def p_namespace_declaration(p):
    """namespace_declaration :  NAMESPACE qualified_identifier namespace_body comma_opt
    """
    p[0] = p[3]

def p_comma_opt(p):
    """comma_opt : empty 
        | STMT_TERMINATOR
    """

def p_qualified_identifier(p):
    """qualified_identifier : IDENTIFIER
        | qualifier IDENTIFIER
    """
    p[0] = {}
    p[0]['code'] = []
    if len(p)==2:
        p[0]['value']=p[1]
    else:
        p[0]['value'] = p[1]['value'] + p[2]
    p[0]['type'] = p[0]['value']
    p[0]['uppertype'] = p[0]['value']
    p[0]['width'] = None
        

def p_qualifier(p):
    """qualifier : IDENTIFIER MEMBERACCESS 
        | qualifier IDENTIFIER MEMBERACCESS 
    """
    p[0] = {}
    if len(p)==3:
        p[0]['value'] = p[1] + p[2]
    else:
        p[0]['value'] = p[1]['value'] + p[2] + p[3]

def p_namespace_body(p):
    """namespace_body : LBRACE using_directives_opt namespace_member_declarations_opt RBRACE
    """
    p[0] = p[3]

def p_using_directives(p):
    """using_directives : using_directive
        | using_directives using_directive
    """
    
def p_using_directive(p):
    """using_directive : using_alias_directive
        | using_namespace_directive
    """
def p_using_alias_directive(p):
    """using_alias_directive : USING IDENTIFIER EQUALS qualified_identifier STMT_TERMINATOR
    """
def p_using_namespace_directive(p):
    """using_namespace_directive : USING namespace_name STMT_TERMINATOR
    """
def p_namespace_member_declarations(p):
    """namespace_member_declarations : namespace_member_declaration
        | namespace_member_declarations namespace_member_declaration
    """
    p[0] = p[1]

def p_namespace_member_declaration(p):
    """namespace_member_declaration : namespace_declaration
        | type_declaration
    """
    p[0] = p[1]

def p_type_declaration(p):
    """type_declaration : class_declarations_opt
        | struct_declaration
        | enum_declaration
        | delegate_declaration
    """
    p[0] = p[1]

# Modifiers
 
def p_modifiers_opt(p):
    """modifiers_opt : empty 
        | modifiers
    """
def p_modifiers(p):
    """modifiers : modifier
        | modifiers modifier
    """
def p_modifier(p):
    """modifier : ABSTRACT
        | EXTERN
        | INTERNAL
        | NEW
        | OVERRIDE
        | PRIVATE
        | PROTECTED
        | PUBLIC
        | READONLY
        | SEALED
        | STATIC
        | UNSAFE
        | VIRTUAL
        | VOLATILE
    """

# C.2.6 Classes 
def p_class_declarations_opt(p):
    """ class_declarations_opt : class_declarations
        | empty
    """
    p[0]=deepcopy(p[1])

def p_class_declarations(p):
    """ class_declarations : class_declaration
        | class_declarations class_declaration
    """
    if len(p) == 2:
        p[0] = deepcopy(p[1])
    else:
        p[0] = deepcopy(p[1]) + deepcopy(p[2])

def p_class_declaration(p):
    """class_declaration :  class_header class_body comma_opt
    """
    p[0] = p[2]
    symbol_table.end_scope()

def p_class_header(p):
    """class_header : CLASS IDENTIFIER COLON class_type 
        | CLASS IDENTIFIER
    """
    if not symbol_table.class_search(p[2]):
        if len(p)==3:
            symbol_table.begin_scope(p[2],'class_type')
        # else:
        #     if symbol_table.class_search(p[4]['type']):
        #         symbol_table.begin_scope(p[2],'class_type',parent_class=p[4]['type'])
        #         parent_class = symbol_table.class_search(p[4]['type'])
    else:
        print("ERROR: class", p[2], "already declared")
        print("Compilation Terminated")
        exit()

def p_class_type(p):
    """ class_type : IDENTIFIER
    """
    p[0] = {}
    p[0]['type']=p[1]
    p[0]['uppertype']='class'

def p_class_body(p):
    """class_body : LBRACE class_member_declarations_opt RBRACE
    """
    p[0] = deepcopy(p[2])

def p_class_member_declarations_opt(p):
    """class_member_declarations_opt : empty 
        | class_member_declarations
    """
    p[0] = p[1]

def p_class_member_declarations(p):
    """class_member_declarations : class_member_declaration
        | class_member_declarations class_member_declaration
    """
    if len(p) == 2:
        p[0] = [deepcopy(p[1])]
    else:
        p[0] = deepcopy(p[1]) + [deepcopy(p[2])]

def p_class_member_declaration(p):
    """class_member_declaration : constant_declaration
        | field_declaration
        | method_declaration
        | operator_declaration
        | constructor_declaration
        | destructor_declaration 
        | type_declaration
    """
    p[0] = deepcopy(p[1])

def p_constant_declaration(p):
    """constant_declaration :  modifiers_opt CONST type constant_declarators STMT_TERMINATOR
    """
def p_field_declaration(p):
    """field_declaration :  modifiers_opt declaration_statement
    """
    p[0] = deepcopy(p[2])

def p_method_declaration(p):
    """method_declaration : method_header method_body
    """
    p[0] = {}
    return_type = p[1]['return_type']
    method_body = p[2]
    p[0]['code'] = ['function, ' + p[1]['value']]
    if p[1]['parameters'] != None:
        for param in p[1]['parameters']:
            p[0]['code'] += ['args, ' + param['value']]
    if 'code' in p[2]:
        p[0]['code'] += p[2]['code']

def p_method_header(p):
    """method_header :  modifiers_opt type qualified_identifier LPAREN formal_parameter_list_opt RPAREN
    """
    p[0] = {}
    p[0]['return_type'] = p[2]
    p[0]['value'] = p[3]['value']
    p[0]['parameters'] = p[5]
    parameter_count =0
    if p[5] != None:
        parameter_count = len(p[5])
    symbol_table.insert_function(p[0]['value'], p[2],p[5], parameter_count)

#def p_void_opt(p):
#    """ void_opt : empty
#        | VOID
#    """

def p_formal_parameter_list_opt(p):
    """formal_parameter_list_opt : empty 
        | formal_parameter_list
    """
    p[0] = p[1]

def p_return_type(p):
    """return_type : type
        | VOID
    """
def p_method_body(p):
    """method_body : block
        | STMT_TERMINATOR
    """
    p[0] = p[1]

def p_formal_parameter_list(p):
    """formal_parameter_list : formal_parameter
        | formal_parameter_list COMMA formal_parameter
    """
    if len(p) == 2:
        p[0] = [deepcopy(p[1])]
    else:
        p[0] = deepcopy(p[1]) + [deepcopy(p[3])]

def p_formal_parameter(p):
    """formal_parameter : fixed_parameter
        | parameter_array
    """
    p[0] = p[1]

def p_fixed_parameter(p):
    """fixed_parameter :  parameter_modifier_opt type IDENTIFIER
    """
    p[0] = {}
    p[0]['type'] = p[2]['type']
    p[0]['uppertype'] = p[2]['uppertype']
    p[0]['value'] = p[3]

def p_parameter_modifier_opt(p):
    """parameter_modifier_opt : empty 
        | REF
        | OUT
    """
def p_parameter_array(p):
    """parameter_array :  PARAMS type IDENTIFIER
    """

def p_operator_declaration(p):
    """operator_declaration :  modifiers_opt operator_declarator operator_body
    """
def p_operator_declarator(p):
    """operator_declarator : overloadable_operator_declarator
        | conversion_operator_declarator
    """
def p_overloadable_operator_declarator(p):
    """overloadable_operator_declarator : type OPERATOR overloadable_operator LPAREN type IDENTIFIER RPAREN
        | type OPERATOR overloadable_operator LPAREN type IDENTIFIER COMMA type IDENTIFIER RPAREN
    """
def p_overloadable_operator(p):
    """overloadable_operator : PLUS 
                            | MINUS 
                            | LNOT 
                            | NOT 
                            | INCREMENT 
                            | DECREMENT 
                            | TRUE 
                            | FALSE
                            | TIMES 
                            | DIVIDE 
                            | MOD 
                            | AND 
                            | OR 
                            | XOR 
                            | LSHIFT 
                            | RSHIFT 
                            | EQ
                            | NE
                            | GT 
                            | LT 
                            | GE
                            | LE
    """
def p_conversion_operator_declarator(p):
    """conversion_operator_declarator : IMPLICIT OPERATOR type LPAREN type IDENTIFIER RPAREN
        | EXPLICIT OPERATOR type LPAREN type IDENTIFIER RPAREN
    """
def p_constructor_declaration(p):
    """constructor_declaration :  modifiers_opt constructor_declarator constructor_body
    """
def p_constructor_declarator(p):
    """constructor_declarator : IDENTIFIER LPAREN formal_parameter_list_opt RPAREN constructor_initializer_opt
    """
def p_constructor_initializer_opt(p):
    """constructor_initializer_opt : empty 
        | constructor_initializer
    """
def p_constructor_initializer(p):
    """constructor_initializer : COLON BASE LPAREN argument_list_opt RPAREN
        | COLON THIS LPAREN argument_list_opt RPAREN
    """

def p_destructor_declaration(p):
    """destructor_declaration :  modifiers_opt NOT IDENTIFIER LPAREN RPAREN block
    """
def p_operator_body(p):
    """operator_body : block
        | STMT_TERMINATOR
    """
def p_constructor_body(p):
    """constructor_body : block
        | STMT_TERMINATOR
    """

# C.2.7 Structs 
def p_struct_declaration(p):
    """struct_declaration :  modifiers_opt STRUCT IDENTIFIER struct_body comma_opt
    """
def p_struct_body(p):
    """struct_body : LBRACE struct_member_declarations_opt RBRACE
    """
def p_struct_member_declarations_opt(p):
    """struct_member_declarations_opt : empty 
        | struct_member_declarations
    """
def p_struct_member_declarations(p):
    """struct_member_declarations : struct_member_declaration
        | struct_member_declarations struct_member_declaration
    """
def p_struct_member_declaration(p):
    """struct_member_declaration : constant_declaration
        | field_declaration
        | method_declaration
        | operator_declaration
        | constructor_declaration
        | type_declaration
    """

# C.2.8 Arrays 
def p_array_initializer(p):
    """array_initializer : LBRACE variable_initializer_list_opt RBRACE
        | LBRACE variable_initializer_list COMMA RBRACE
    """
    p[0] = deepcopy(p[2])

def p_variable_initializer_list_opt(p):
    """variable_initializer_list_opt : empty 
        | variable_initializer_list
    """
    p[0] = deepcopy(p[1])

def p_variable_initializer_list(p):
    """variable_initializer_list : variable_initializer
        | variable_initializer_list COMMA variable_initializer
    """
    if len(p) == 2:
        p[0] = [deepcopy(p[1])]
    else:
        p[0] = deepcopy(p[1]) + [deepcopy(p[3])]

# C.2.10 Enums 
def p_enum_declaration(p):
    """enum_declaration :  modifiers_opt ENUM IDENTIFIER enum_base_opt enum_body comma_opt
    """
def p_enum_base_opt(p):
    """enum_base_opt : empty 
        | enum_base
    """
def p_enum_base(p):
    """enum_base : COLON integral_type
    """
def p_enum_body(p):
    """enum_body : LBRACE enum_member_declarations_opt RBRACE
        | LBRACE enum_member_declarations COMMA RBRACE
    """
def p_enum_member_declarations_opt(p):
    """enum_member_declarations_opt : empty 
        | enum_member_declarations
    """
def p_enum_member_declarations(p):
    """enum_member_declarations : enum_member_declaration
        | enum_member_declarations COMMA enum_member_declaration
    """
def p_enum_member_declaration(p):
    """enum_member_declaration :  IDENTIFIER
        |  IDENTIFIER EQUALS constant_expression
    """

# C.2.11 Delegates 
def p_delegate_declaration(p):
    """delegate_declaration :  modifiers_opt DELEGATE return_type IDENTIFIER LPAREN formal_parameter_list_opt RPAREN STMT_TERMINATOR
    """

# Miscelleneous
def p_empty(p):
    """empty :"""
    p[0] = None

def math_ops(p0,p1,p3,operation):
        p0 = {}
        t = symbol_table.maketemp('int', symbol_table.curr_table)
        p0['value'] = t
        p0['code'] = p1['code'] + p3['code']
        p0['code'] += [operation + ", " + p0['value'] +  ", " + p1['value'] + ", " + p3['value']]
        return p0,p1,p3

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!", p)

###################################################################################################
# Build the parser now
parser = yacc.yacc(start='compilation_unit', debug=True, optimize=False)

# Read the input program
inputfile = open(filename, 'r')
data = inputfile.read()
result = parser.parse(data, debug=0)
