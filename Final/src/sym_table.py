#!/usr/bin/python3
# Symbol Table Implementation

from copy import deepcopy


base_table = None
labelnum=-1
tempnum=-1
        
def genlabel():
    global labelnum
    labelnum+=1
    return "L"+str(labelnum)

def generatetmp():
    global tempnum
    tempnum+=1
    return "t"+str(tempnum)


class table:
    def __init__(self, prev = None):
        self.hash = {}
        self.parent = prev
        self.children = []

    def insert_variable(self, var_type, identifier):
        self.hash[identifier] = {}
        self.hash[identifier]['type'] = var_type
        self.hash[identifier]['uppertype'] = 'variable'

    def insert_temp(self, var_type, identifier):
        if identifier not in self.hash:     
            self.hash[identifier] = {}
            self.hash[identifier]['type'] = var_type
            self.hash[identifier]['uppertype'] = 'temporary'
            return True 
        else:
            return False

    def insert_array(self, var_type, identifier,width):
        self.hash[identifier] = {}
        self.hash[identifier]['type'] = var_type
        self.hash[identifier]['uppertype'] = 'array'
        self.hash[identifier]['width'] = width

    def insert_function(self, method_name, return_type, param_types, param_num):
        if method_name not in self.hash:
            self.hash[method_name] = {}
            self.hash[method_name]['type'] = return_type
            self.hash[method_name]['uppertype'] = 'function'
            self.hash[method_name]['arg_num'] = param_num
            self.hash[method_name]['arg_types'] = param_types
        
    def lookup_in_this(self, identifier):
        if identifier in self.hash:
            return self.hash[identifier]
        else:
            return None


class env:
    def __init__(self):
        self.curr_table = table(None)
        global base_table
        base_table = self.curr_table

    def maketemp(self, temp_type, table):
        while True:
            name = generatetmp()
            if table.insert_temp(temp_type, name)==True:
                return name

    def newlabel(self):
        label = genlabel()
        return label

    def begin_scope(self):
        new_table = table(self.curr_table)
        self.curr_table.children.append(new_table)
        self.curr_table = new_table
        return self.curr_table

    def end_scope(self):
        self.curr_table = self.curr_table.parent

    def insert_variable(self, var_type, identifier):
        self.curr_table.insert_variable(var_type, identifier)

    def insert_temp(self, var_type, identifier):
        self.curr_table.insert_temp(var_type, identifier)

    def insert_array(self, var_type, identifier,width):
        self.curr_table.insert_array(var_type, identifier,width)

    def lookup(self, identifier, table):
        while table!=None:
            res = table.lookup_in_this(identifier)
            if res != None:
                return res
            table = table.parent
        return None

    def insert_function(self, method_name, return_type, param_types, param_num):
        self.curr_table.insert_function(method_name, return_type, param_types, param_num)
        
    def lookup_in_this(self, identifier):
        self.curr_table.lookup_in_this(identifier)
