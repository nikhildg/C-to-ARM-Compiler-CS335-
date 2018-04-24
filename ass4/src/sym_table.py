#!/usr/bin/python3
# Symbol Table Implementation

from copy import deepcopy
from collections import OrderedDict

base_table = None
labelnum=-1
tempnum=-1
Id=-1
     
def generateid():
    global Id
    Id +=1
    return "i"+str(Id)

def genlabel():
    global labelnum
    labelnum+=1
    return "L"+str(labelnum)

def generatetmp():
    global tempnum
    tempnum+=1
    return "t"+str(tempnum)


class table:
    def __init__(self, prev=None,scope_name=None,scope_type=None,return_type=None,Class=None,parent_class=None):
        self.hash = {}
        self.children = []
        self.width = 0
        self.max_width = 0
        self.parent = prev
        self.type = scope_type
        self.Class = Class
        self.name = scope_name
        self.parent_class = parent_class
        self.return_type = return_type
        self.offset = 0

    def insert_variable(self, var_type, identifier,uppertype='variable',var_width=-1):
        var_width = self.get_width(var_type,uppertype,int(var_width))
        self.hash[identifier] = {}
        self.hash[identifier]['type'] = var_type
        self.hash[identifier]['uppertype'] = uppertype
        self.offset += var_width
        self.width+=var_width

    def insert_temp(self, var_type, identifier,uppertype='variable',var_width=-1):
        if identifier not in self.hash:     
            var_width = self.get_width(var_type,uppertype,int(var_width))
            loc = generatetmp()
            offset = self.offset
            self.hash[identifier] = {}
            self.hash[identifier]['type'] = var_type
            self.hash[identifier]['uppertype'] = 'temporary'
            self.offset += var_width
            self.width += var_width
            return loc
        else:
            return False

    def get_width(self,var_type,uppertype='variable',width=-1):
        dic = {"int":4,"double":8,"bool":4,"char":4, "void":0}
        if uppertype=='variable':
            return dic[var_type]
        elif uppertype=='array':
            return width*dic[var_type]
        elif uppertype == 'class':
            return width

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
        curr_table = self
        while curr_table!= None:
            if identifier in self.hash:
                return self.hash[identifier]
            curr_table = curr_table.parent
        return None

    def class_search(self,class_name):
        for child in base_table.children:
            if child.type=='class_type' and child.name==class_name:
                return child
            return None

class env:
    def __init__(self):
        self.curr_table = table(None)
        global base_table
        base_table = self.curr_table

    def Mainclass(self):
        node_searched=None
        count_main=0
        main_method=None
        for node in base_table.children:
            if node.type == 'class_type':
                for child in node.children:
                    if child.type == 'method_type' and child.name == 'Main':
                        node_searched = node
                        main_method = child
                        count_main+=1
        return node_searched, main_method, count_main

    def maketemp(self, temp_type, table):
        # while True:
        #     name = generatetmp()
        #     if table.insert_temp(temp_type, name)==True:
        #         return name
        return self.curr_table.insert_temp(temp_type, generatetmp())

    def newlabel(self):
        label = genlabel()
        return label

    def begin_scope(self, scope_name='undefined', scope_type='block',return_type=None,Class=None,parent_class=None):
        offset = self.curr_table.offset
        new_table = table(self.curr_table,scope_name,scope_type,return_type,Class,parent_class)
        if new_table.type=='block':
            new_table.offset=offset
        self.curr_table.children.append(new_table)
        self.curr_table = new_table
        return self.curr_table

    def class_search(self,class_name):
        return self.curr_table.class_search(class_name)

    def end_scope(self):
        if self.curr_table.type=='class_type':
            hash=self.curr_table.hash
            self.curr_table = self.curr_table.parent
            self.curr_table.hash.update(hash)
        else:
            curr_width = self.curr_table.width=max(self.curr_table.max_width,self.curr_table.width)
            hash=self.curr_table.hash
            self.curr_table = self.curr_table.parent
            self.curr_table.max_width = max(self.curr_table.max_width,self.curr_table.width)
            self.curr_table.hash.update(hash)
        
    def insert_variable(self, var_type, identifier,uppertype='variable',var_width=-1):
        self.curr_table.insert_variable(var_type, identifier, uppertype, var_width)

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
