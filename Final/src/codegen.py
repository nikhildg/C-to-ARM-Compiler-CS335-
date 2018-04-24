#!/usr/bin/python3

import sys

# List of general purpose registers 
reglist = ['R5','R6','R7','R8','R9','R10','R12']

# Construct the register descriptor table
registers = {}
registers = registers.fromkeys(reglist)

# Variable 
varlist = []
addressDescriptor = {}
relcount = 1
# Three address code keywords
tackeywords = ['ifgoto', 'goto', 'return', 'call', 'print', 'label', 'function' , 'exit' , 'args', 'param',
                '<=', '>=', '==', '>', '<', '>>', '<<', '!=', '=', 
                '+', '-', '*', '/', '%', 
                '&&', '||', '~' ]
mathops = ['+', '-', '*', '/', '%']
div_bool = False


#Float not considered only integers
def isnumber(num):
    t = num.isdigit() or (num[1:].isdigit() and num[0] == "-")
    return t


# Sets the register descriptor entry as per the arguments
def setregister(register, content):
    registers[register] = content

# Returns the location of the variable from the addrss descriptor table
def getlocation(variable):
    return addressDescriptor[variable]

# Sets the location entry in the adrdrss decriptor for a variable 
def setlocation(variable, location):
    addressDescriptor[variable] = location

# Returns the nextuse of the variable
def nextuse(variable, line):
    return nextuseTable[line-1][variable]

def getReg(var, line, assembly):
    #if variable in register
    for key in registers.keys():
        if registers[key] == var:
            return key,assembly
    #search for empty register
    for key in registers.keys():
        if registers[key] == None:
            return key,assembly
    #spilling implemented here
    #search dead variable
    # assembly+="-------------spilled-------" +var+"\n"
    #print(registers)
    next_use = nextuseTable[line - 1]
    for key in next_use.keys():
        if next_use[key][0]=="dead":
            for regspill in registers.keys():
                if registers[regspill] == key:
                    assembly = assembly + "LDR R1, ="+key+"\n"
                    assembly = assembly + "STR " + regspill + ", [R1]" + "\n"
                    setlocation(key, "mem")
                    return regspill,assembly
    #search None next use variable
    temp=0
    for key in next_use.keys():
        if next_use[key][1]==None:
            for regspill in registers.keys():
                if registers[regspill] == key:
                    assembly = assembly + "LDR R1, ="+key+"\n"
                    assembly = assembly + "STR " + regspill + ", [R1]" + "\n"
                    setlocation(key, "mem")
                    return regspill,assembly
        elif next_use[key][1]>=temp:
            spill_var=key
            temp=next_use[key][1]
    #variable with highest next use
    for regspill in registers.keys():
        if registers[regspill] == spill_var:
            assembly = assembly + "LDR R1, ="+spill_var+"\n"
            assembly = assembly + "STR " + regspill + ", [R1]" + "\n"
            setlocation(spill_var, "mem")
            return regspill,assembly

# The function to translate a single line tac to x86 assembly
def translate(instruction):
    global relcount
    global div_bool
    assembly = ""
    line = int(instruction[0])
    # assembly = assembly + str(line) + "\n"
    operator = instruction[1]
    # Generating assembly code if the tac is a print
    # Generating assembly code if the tac is a mathematical operation

    if operator in mathops:
        result = instruction[2]
        operand1 = instruction[3]
        operand2 = instruction[4]
        if operator == '+':
            if isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest,assembly = getReg(result, line, assembly)
                assembly = assembly + "MOV " + regdest + ", #" + operand1 + "\n"
                assembly = assembly + "ADD " + regdest + ", " + regdest + ", #" + operand2 + "\n"
                # Update the address descriptor entry for result variable to say where it is stored no
                setregister(regdest, result)
                setlocation(result, regdest)
            elif isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc2 = getlocation(operand2)
                # Move the first operand to the destination register
                if loc2 != "mem":
                    assembly = assembly + "MOV "  + regdest + ", "  + loc2 + "\n"
                else:
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + regdest + ", [R1]"  + "\n"
                assembly = assembly + "ADD " + regdest + ", " +regdest + ", #" + operand1 + "\n"
                setregister(regdest, result)
                setlocation(result, regdest)
            elif not isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc1 = getlocation(operand1)
                # Move the first operand to the destination register
                if loc1 != "mem":
                    assembly = assembly + "MOV "  + regdest + ", "  + loc1 + "\n"
                else:
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + regdest + ", [R1]"  + "\n"
                assembly = assembly + "ADD " + regdest + ", " +regdest + ", #" + operand2 + "\n"
                setregister(regdest, result)
                setlocation(result, regdest)
            elif not isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                # Get the locations of the operands
                loc1 = getlocation(operand1)
                loc2 = getlocation(operand2)
                if loc1 != "mem" and loc2 != "mem":
                    assembly = assembly + "ADD " + regdest + ", " + loc1 + ", " + loc2 + "\n"
                elif loc1 == "mem" and loc2 != "mem":
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + regdest + ", [R1]"   + "\n"
                    assembly = assembly + "ADD " + regdest + ", " + regdest + ", " + loc2 + "\n"
                elif loc1 != "mem" and loc2 == "mem":
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + regdest + ", [R1]"   + "\n"
                    assembly = assembly + "ADD " + regdest + ", " + regdest + ", " + loc1 + "\n"
                elif loc1 == "mem" and loc2 == "mem":
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR " + regdest + ", [R1]" + "\n"
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR " + "R2" + ", " + "[R1]\n"
                    assembly = assembly + "ADD " + regdest + ", " + regdest + ", " + "R2"+ "\n"
                # Update the register descriptor entry for regdest to say that it contains the result
                setregister(regdest, result)
                # Update the address descriptor entry for result variable to say where it is stored now
                setlocation(result, regdest)

        # Subtraction
        elif operator == '-':
            if isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                assembly = assembly + "MOV " + regdest + ", #" + operand1 + "\n"
                assembly = assembly + "SUBS " + regdest + ", " + regdest + ", #" + operand2 + "\n" 
                # Update the address descriptor entry for result variable to say where it is stored no
                setregister(regdest, result)
                setlocation(result, regdest)
            elif isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc2 = getlocation(operand2)
                # Move the first operand to the destination register
                assembly = assembly + "MOV "  + regdest + ", #"  + operand1 + "\n" 
                
                if loc2 != "mem":
                    assembly = assembly + "SUBS " + regdest + ", " + regdest + ", " + loc2 + "\n" 
                else:
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR " + "R2" + ", " + "[R1]\n"
                    assembly = assembly + "SUBS " + regdest + ", " + regdest + ", " + "R2" + "\n" 
                setregister(regdest, result)
                setlocation(result, regdest)                
            elif not isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc1 = getlocation(operand1)
                # Move the first operand to the destination register
                if loc1 != "mem":
                    assembly = assembly + "MOV "  + regdest + ", "  + loc1 + "\n" 
                else:
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + regdest + ", [R1]"  + "\n" 
                assembly = assembly + "SUBS " + regdest + ", " +regdest + ", #" + operand2 + "\n" 
                setregister(regdest, result)
                setlocation(result, regdest)                
            elif not isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                # Get the locations of the operands
                loc1 = getlocation(operand1)
                loc2 = getlocation(operand2)
                if loc1 != "mem" and loc2 != "mem":
                    assembly = assembly + "SUBS " + regdest + ", " + loc1 + ", " + loc2 + "\n" 
                elif loc1 == "mem" and loc2 != "mem":
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + regdest + ", [R1]"  + "\n" 
                    assembly = assembly + "SUBS " + regdest + ", " + regdest + ", " + loc2 + "\n" 
                elif loc1 != "mem" and loc2 == "mem":
                    assembly = assembly + "MOV " + regdest + ", " + loc1 + "\n" 
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR " + "R2" + ", " + "[R1]\n"
                    assembly = assembly + "SUBS " + regdest + ", " + regdest + ", " + "R2" + "\n" 
                elif loc1 == "mem" and loc2 == "mem":
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + regdest + ", [R1]" + "\n" 
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR " + "R2" + ", " + "[R1]\n"
                    assembly = assembly + "SUBS " + regdest + ", " + regdest + ", " + "R2"+ "\n"                     
                # Update the register descriptor entry for regdest to say that it contains the result
                setregister(regdest, result)
                # Update the address descriptor entry for result variable to say where it is stored now
                setlocation(result, regdest)

        # Multiplication
        elif operator == '*':
            if isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                assembly = assembly + "LDR " + "R1, =#" + operand1 + "\n" 
                assembly = assembly + "LDR " + "R2, =#" + operand2 + "\n" 
                assembly = assembly + "MUL " + regdest + ", " + "R1" + ", " + "R2" + "\n" 
                # Update the address descriptor entry for result variable to say where it is stored no
                setregister(regdest, result)
                setlocation(result, regdest)
            elif isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc2 = getlocation(operand2)
                # Move the first operand to the destination register
                assembly = assembly + "LDR " + "R1, =#" + operand1 + "\n" 
                if loc2 != "mem":
                    assembly = assembly + "MUL " + regdest + ", " +loc2 + ", R1" + "\n" 
                else:
                    assembly = assembly + "LDR " + "R0" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + "R2" + ", [R0]"  + "\n" 
                    assembly = assembly + "MUL " + regdest + ", " +"R2" + ", R1" + "\n" 
                setregister(regdest, result)
                setlocation(result, regdest)                
            elif not isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc1 = getlocation(operand1)
                # Move the first operand to the destination register
                assembly = assembly + "LDR " + "R1, =#" + operand2 + "\n" 
                
                if loc1 != "mem":
                    assembly = assembly + "MUL " + regdest + ", " +loc1 + ", R1" + "\n" 
                else:
                    assembly = assembly + "LDR " + "R0" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR " + "R2" + ", [R0]" + "\n" 
                    assembly = assembly + "MUL " + regdest + ", " +"R2" + ", R1" + "\n" 
                setregister(regdest, result)
                setlocation(result, regdest)                
            elif not isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                # Get the locations of the operands
                loc1 = getlocation(operand1)
                loc2 = getlocation(operand2)
                if loc1 != "mem" and loc2 != "mem":
                    assembly = assembly + "MUL " + regdest + ", " + loc1 + ", " + loc2 + "\n" 
                elif loc1 == "mem" and loc2 != "mem":
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + "R0" + ", [R1]"  + "\n" 
                    assembly = assembly + "MUL " + regdest + ", " + "R0" + ", " + loc2 + "\n" 
                elif loc1 != "mem" and loc2 == "mem":
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + "R0" + ", [R1]"  + "\n" 
                    assembly = assembly + "MUL " + regdest + ", " + "R0" + ", " + loc1 + "\n" 
                elif loc1 == "mem" and loc2 == "mem":
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR " + "R0" + ", [R1]" + "\n" 
                    assembly = assembly + "LDR " + "R1" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR " + "R2" + ", " + "[R1]\n"
                    assembly = assembly + "MUL " + regdest + ", " + "R0" + ", " + "R2"+ "\n" 
                # Update the register descriptor entry for regdest to say that it contains the result
                setregister(regdest, result)
                # Update the address descriptor entry for result variable to say where it is stored now
                setlocation(result, regdest)

        #Division
        elif operator == '/':
            div_bool=True
            if isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                assembly = assembly + "LDR " + "R0" + ", =#" + operand1 + "\n"
                assembly = assembly + "LDR " + "R1" + ", =#" + operand2 + "\n"
                assembly = assembly + "BL unsigned_longdiv" + "\n"
                assembly = assembly + "MOV " + regdest + ", " + "R2" + "\n"
                # Update the address descriptor entry for result variable to say where it is stored no
                setregister(regdest, result)
                setlocation(result, regdest)
            elif isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc2 = getlocation(operand2)
                assembly = assembly + "LDR " + "R0" + ", =#" + operand1 + "\n"
                if loc2 != "mem":
                    assembly = assembly + "MOV " + "R1" + ", " + loc2 + "\n"
                else:
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + "R1" + ", [R2]"  +  + "\n"
                assembly = assembly + "BL unsigned_longdiv" + "\n"
                assembly = assembly + "MOV " + regdest + ", " + "R2" + "\n"
                setregister(regdest, result)
                setlocation(result, regdest)
            elif not isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc1 = getlocation(operand1)
                assembly = assembly + "LDR " + "R1" + ", =#" + operand2 + "\n"
                if loc1 != "mem":
                    assembly = assembly + "MOV " + "R0" + ", " + loc1 + "\n"
                else:
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + "R0" + ", [R2]"  + "\n"
                assembly = assembly + "BL unsigned_longdiv" + "\n"
                assembly = assembly + "MOV " + regdest + ", " + "R2" + "\n"
                setregister(regdest, result)
                setlocation(result, regdest)
            elif not isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                # Get the locations of the operands
                loc1 = getlocation(operand1)
                loc2 = getlocation(operand2)
                if loc1 != "mem" and loc2 != "mem":
                    assembly = assembly + "MOV " + "R0" +  ", " + loc1 + "\n" 
                    assembly = assembly + "MOV " + "R1" +  ", " + loc2 + "\n" 
                elif loc1 == "mem" and loc2 != "mem":
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + "R0" + ", [R2]"  + "\n"
                    assembly = assembly + "MOV " + "R1" +  ", " + loc2 + "\n"
                elif loc1 != "mem" and loc2 == "mem":
                    assembly = assembly + "MOV " + "R0" +  ", " + loc1 + "\n" 
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + "R1" + ", [R2]"  + "\n"
                elif loc1 == "mem" and loc2 == "mem":
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + "R0" + ", [R2]"  + "\n"
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + "R1" + ", [R2]"  + "\n"
                assembly = assembly + "BL unsigned_longdiv" + "\n"            
                assembly = assembly + "MOV " + regdest + ", " + "R2" + "\n"
                # Update the register descriptor entry for regdest to say that it contains the result
                setregister(regdest, result)
                setlocation(result, regdest)

        #Modulo
        elif operator == '%':
            div_bool=True
            if isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                assembly = assembly + "LDR " + "R0" + ", =#" + operand1 + "\n"
                assembly = assembly + "LDR " + "R1" + ", =#" + operand2 + "\n"
                assembly = assembly + "BL unsigned_longdiv" + "\n"
                assembly = assembly + "MOV " + regdest + ", " + "R3" + "\n"
                # Update the address descriptor entry for result variable to say where it is stored no
                setregister(regdest, result)
                setlocation(result, regdest)
            elif isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc2 = getlocation(operand2)
                assembly = assembly + "LDR " + "R0" + ", =#" + operand1 + "\n"
                if loc2 != "mem":
                    assembly = assembly + "MOV " + "R1" + ", " + loc2 + "\n"
                else:
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + "R1" + ", [R2]"   + "\n"
                assembly = assembly + "BL unsigned_longdiv" + "\n"
                assembly = assembly + "MOV " + regdest + ", " + "R3" + "\n"
                setregister(regdest, result)
                setlocation(result, regdest)
            elif not isnumber(operand1) and isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                loc1 = getlocation(operand1)
                assembly = assembly + "LDR " + "R1" + ", =#" + operand2 + "\n"
                if loc1 != "mem":
                    assembly = assembly + "MOV " + "R0" + ", " + loc1 + "\n"
                else:
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + "R0" + ", [R2]"   + "\n"
                assembly = assembly + "BL unsigned_longdiv" + "\n"
                assembly = assembly + "MOV " + regdest + ", " + "R3" + "\n"
                setregister(regdest, result)
                setlocation(result, regdest)
            elif not isnumber(operand1) and not isnumber(operand2):
                # Get the register to store the result
                regdest ,assembly = getReg(result, line, assembly)
                # Get the locations of the operands
                loc1 = getlocation(operand1)
                loc2 = getlocation(operand2)
                if loc1 != "mem" and loc2 != "mem":
                    assembly = assembly + "MOV " + "R0" +  ", " + loc1 + "\n" 
                    assembly = assembly + "MOV " + "R1" +  ", " + loc2 + "\n"
                elif loc1 == "mem" and loc2 != "mem":
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + "R0" + ", [R2]"   + "\n"
                    assembly = assembly + "MOV " + "R1" +  ", " + loc2 + "\n"
                elif loc1 != "mem" and loc2 == "mem":
                    assembly = assembly + "MOV " + "R0" +  ", " + loc1 + "\n"
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + "R1" + ", [R2]"  +  + "\n"
                elif loc1 == "mem" and loc2 == "mem":
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand1 + "\n"
                    assembly = assembly + "LDR "  + "R0" + ", [R2]"   + "\n"
                    assembly = assembly + "LDR " + "R2" + ", " + "=" + operand2 + "\n"
                    assembly = assembly + "LDR "  + "R1" + ", [R2]"   + "\n"
                assembly = assembly + "BL unsigned_longdiv" + "\n"           
                assembly = assembly + "MOV " + regdest + ", " + "R3" + "\n"
                # Update the register descriptor entry for regdest to say that it contains the result
                setregister(regdest, result)
                setlocation(result, regdest)

    elif operator == "&&":
        #Line, &&, result, op1, op2
        result = instruction[2]
        operand1 = instruction[3]       #num
        operand2 = instruction[4]       #count
        T = "T"+str(relcount)
        NT = "NT"+str(relcount)
       	if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
            assembly = assembly + "LDR " + "R1" + ", =#" + operand2 +  "\n"
            assembly = assembly + "AND " + regdest + ", " + "R0, " + "R1"+ "\n" 
        elif isnumber(operand1) and not isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
            if loc2 != "mem":
                assembly = assembly + "AND " + regdest + ", " + "R0, " + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 +  "\n"
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n"
                assembly = assembly + "AND " + regdest + ", " + "R0, " + ", R2"  + "\n" 
        elif not isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move the first operand to the destination register
            if loc1 != "mem":
                assembly = assembly + "LDR " + "R0" + ", =#" + operand2 +  "\n" 
                assembly = assembly + "AND " + regdest + ", " + loc1 + ", R0"  + "\n"
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "LDR " + "R0" + ", =#" + operand2 +  "\n" 
                assembly = assembly + "AND " + regdest + ", " + "R2"  + ", R0" + "\n" 
        elif not isnumber(operand1) and not isnumber(operand2):
            #case result = a && b
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                #result = a and result = result << b
                assembly = assembly + "AND " + regdest + ", " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "AND " + regdest + ", " + "R2" + ", " + loc2 + "\n" 
            
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "AND " + regdest + ", " + loc1 + ", " + "R2" + "\n" 
                # assembly = assembly + "MOV " + regdest +  ", " + loc1 + "LSL " + operand2 + "\n" 
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 +  "\n" 
                assembly = assembly + "LDR " + "R1" + ", " + "[R0]" +  "\n" 
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R0]" +  "\n"         
                assembly = assembly + "AND " + regdest + ", " + "R1" + ", " + "R2" + "\n"                    
        # Update the register descriptor entry for regdest to say that it contains the result
        assembly = assembly + "LDR " + "R0, "+ "=#0" + "\n"
        assembly = assembly + "CMP " + regdest + ", R0" + "\n" 
	# Update the register descriptor entry for regdest to say that it contains the result
        assembly = assembly + "BNE " + T + "\n"
        assembly = assembly + "MOV " + regdest + ", #0" +  "\n" 
        assembly = assembly + "B " + NT + "\n"
        assembly = assembly + T + ":" + "\n"
        assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
        assembly = assembly + NT + ":" + "\n"
        setregister(regdest, result)
        # Update the address descriptor entry for result variable to say where it is stored now
        setlocation(result, regdest)
        relcount = relcount + 1	
	
    elif operator == "||":
        #Line, &&, result, op1, op2
        result = instruction[2]
        operand1 = instruction[3]       #num
        operand2 = instruction[4]       #count
        T = "T"+str(relcount)
        NT = "NT"+str(relcount)
       	if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
            assembly = assembly + "LDR " + "R1" + ", =#" + operand2 +  "\n"
            assembly = assembly + "ORR " + regdest + ", " + "R0, " + "R1"+ "\n" 
        elif isnumber(operand1) and not isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
            if loc2 != "mem":
                assembly = assembly + "ORR " + regdest + ", " + "R0, " + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n"
                assembly = assembly + "ORR " + regdest + ", " + "R0, " + ", R2"  + "\n"
        elif not isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move the first operand to the destination register
            if loc1 != "mem":
                assembly = assembly + "LDR " + "R0" + ", =#" + operand2 +  "\n" 
                assembly = assembly + "ORR " + regdest + ", " + loc1 + ", R0"  + "\n"
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 +  "\n"
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "LDR " + "R0" + ", =#" + operand2 +  "\n" 
                assembly = assembly + "ORR " + regdest + ", " + "R2"  + ", R0" + "\n"
        elif not isnumber(operand1) and not isnumber(operand2):
            #case result = a && b
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                #result = a and result = result << b
                assembly = assembly + "ORR " + regdest + ", " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "ORR " + regdest + ", " + "R2" + ", " + loc2 + "\n" 
            
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "ORR " + regdest + ", " + loc1 + ", " + "R2" + "\n" 
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 +  "\n" 
                assembly = assembly + "LDR " + "R1" + ", " + "[R0]" +  "\n" 
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R0]" +  "\n" 
                assembly = assembly + "ORR " + regdest + ", " + "R1" + ", " + "R2" + "\n" 
        # Update the register descriptor entry for regdest to say that it contains the result
        assembly = assembly + "LDR " + "R0, "+ "=#0" + "\n"
        assembly = assembly + "CMP " + regdest + ", R0" + "\n" 
	# Update the register descriptor entry for regdest to say that it contains the result
        assembly = assembly + "BNE " + T + "\n"
        assembly = assembly + "MOV " + regdest + ", #0" +  "\n" 
        assembly = assembly + "B " + NT + "\n"
        assembly = assembly + T + ":" + "\n"
        assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
        assembly = assembly + NT + ":" + "\n"
        setregister(regdest, result)
        # Update the address descriptor entry for result variable to say where it is stored now
        setlocation(result, regdest)
        relcount = relcount + 1	
	
    elif operator == "~":
        #Line, not, result, op1
        result = instruction[2]
        operand1 = instruction[3]       #num
        if isnumber(operand1):
            #Case : result = !(1)
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
            assembly = assembly + "NEG " + regdest + ", " + "R0, " + "\n" 
            # Update the address descriptor entry for result variable to say where it is stored no
            setregister(regdest, result)
            setlocation(result, regdest)
        elif not isnumber(operand1):
            #case result = !(a)
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move a to regdest, result = a
            if loc1 != "mem":
                assembly = assembly + "MOV " + regdest + ", " + loc1 + "\n" 
            else:
                assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
                assembly = assembly + "MOV " + regdest + ", " + "R0" + "\n" 
            # Perform Logical and result = !(result)
            assembly = assembly + "NEG " + regdest + ", " + regdest + "\n" 
            setregister(regdest, result)
            setlocation(result, regdest)

    # Generating code for assignment operations
    elif operator == '=':
        #assembly+="--------add\n"
        destination = instruction[2]
        source = instruction[3]
        loc1 = getlocation(destination)
        regdest ,assembly = getReg(destination, line, assembly)
        #assembly+="************\n"
        # If the source is a literal then we can just move it to the destination
        if isnumber(source):
            assembly = assembly + "LDR " + regdest + ", =#" + source + "\n" 
        else:
            # If the source in the memory
            loc2 = getlocation(source)
            if  loc2 == "mem":
                assembly = assembly + "LDR R1" + ", =" + source + "\n" 
                assembly = assembly + "LDR " + regdest + ", [R1]" + "\n" 
                # Update the address descriptor entry for result variable to say where it is stored no
            # If the source is in a register
            elif loc2 != "mem":
                assembly = assembly + "MOV " + regdest + ", " + loc2 + "\n" 
                # Update the address descriptor entry for result variable to say where it is stored no
        setregister(regdest, destination)
        setlocation(destination, regdest)
        #assembly+="----end\n"
    #Logical Left shift
    elif operator == "<<":
        result = instruction[2]
        operand1 = instruction[3]       #num
        operand2 = instruction[4]       #count
        if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
            assembly = assembly + "LDR " + "R1" + ", =#" + operand2 +  "\n" 
            assembly = assembly + "LSL " + regdest + ", " + "R0, " + "R1"+ "\n"
            # Update the address descriptor entry for result variable to say where it is stored no
            setregister(regdest, result)
            setlocation(result, regdest)
        elif isnumber(operand1) and not isnumber(operand2):
            #case result = 5 << x
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move 5 to result, result = 5
            #perform left shift, result = result << x
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
            if loc2 != "mem":
                assembly = assembly + "LSL " + regdest + ", " + "R0, " + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "LSL " + regdest + ", " + "R0, " + ", R2"  + "\n" 
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and isnumber(operand2):
            #case result = a << 2
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move a to regdest, result = a
            if loc1 != "mem":
                assembly = assembly + "LDR " + "R0" + ", =#" + operand2 +  "\n" 
                assembly = assembly + "LSL " + regdest + ", " + loc1 + ", R0"  + "\n"
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 +  "\n"
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n"
                assembly = assembly + "LDR " + "R0" + ", =#" + operand2 +  "\n" 
                assembly = assembly + "LSL " + regdest + ", " + "R2"  + ", R0" + "\n" 
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and not isnumber(operand2):
            #case result = a << b
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                #result = a and result = result << b
                assembly = assembly + "LSL " + regdest + ", " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n"
                assembly = assembly + "LSL " + regdest + ", " + "R2" + ", " + loc2 + "\n"
            
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "LSL " + regdest + ", " + loc1 + ", " + "R2" + "\n"
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 +  "\n"
                assembly = assembly + "LDR " + "R1" + ", " + "[R0]" +  "\n" 
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R0]" +  "\n" 
                assembly = assembly + "LSL " + regdest + ", " + "R1" + ", " + "R2" + "\n" 
            # Update the register descriptor entry for regdest to say that it contains the result
            setregister(regdest, result)
            # Update the address descriptor entry for result variable to say where it is stored now
            setlocation(result, regdest)

    #Logical Right shift
    elif operator == ">>":
        result = instruction[2]
        operand1 = instruction[3]       #num
        operand2 = instruction[4]       #count
        if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
            assembly = assembly + "LDR " + "R1" + ", =#" + operand2 +  "\n"
            assembly = assembly + "LSR " + regdest + ", " + "R0, " + "R1"+ "\n"
            # Update the address descriptor entry for result variable to say where it is stored no
            setregister(regdest, result)
            setlocation(result, regdest)
        elif isnumber(operand1) and not isnumber(operand2):
            #case result = 5 << x
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move 5 to result, result = 5
            #perform left shift, result = result << x
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 +  "\n" 
            if loc2 != "mem":
                assembly = assembly + "LSR " + regdest + ", " + "R0, " + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "LSR " + regdest + ", " + "R0, " + ", R2"  + "\n" 
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and isnumber(operand2):
            #case result = a << 2
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move a to regdest, result = a
            if loc1 != "mem":
                assembly = assembly + "LDR " + "R0" + ", =#" + operand2 +  "\n" 
                assembly = assembly + "LSR " + regdest + ", " + loc1 + ", R0"  + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n"
                assembly = assembly + "LDR " + "R0" + ", =#" + operand2 +  "\n" 
                assembly = assembly + "LSR " + regdest + ", " + "R2"  + ", R0" + "\n" 
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and not isnumber(operand2):
            #case result = a << b
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                #result = a and result = result << b
                assembly = assembly + "LSR " + regdest + ", " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n"
                assembly = assembly + "LSR " + regdest + ", " + "R2" + ", " + loc2 + "\n" 
            
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R1]" +  "\n" 
                assembly = assembly + "LSR " + regdest + ", " + loc1 + ", " + "R2" + "\n" 
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 +  "\n" 
                assembly = assembly + "LDR " + "R1" + ", " + "[R0]" +  "\n"
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 +  "\n" 
                assembly = assembly + "LDR " + "R2" + ", " + "[R0]" +  "\n" 
                assembly = assembly + "LSR " + regdest + ", " + "R1" + ", " + "R2" + "\n" 
            # Update the register descriptor entry for regdest to say that it contains the result
            setregister(regdest, result)
            # Update the address descriptor entry for result variable to say where it is stored now
            setlocation(result, regdest)

    elif operator == "print":
        assembly = assembly + "push {ip, lr}\n"
        operand = instruction[2]
        if not isnumber(operand):
            loc = getlocation(operand)
            if not loc == "mem":
                assembly = assembly + "LDR R0, =str\n"
                assembly = assembly + "MOV R1," + loc + "\n"
                assembly = assembly + "BL printf\n"
            else: 
                assembly = assembly + "LDR R0, =str\n"
                assembly = assembly + "LDR " + "R2" + ",=" + operand+"\n"
                assembly = assembly + "LDR R1" + " , [R2]\n"
                assembly = assembly + "BL printf\n" 
        else:
            assembly = assembly + "LDR R0, =str\n"
            assembly = assembly + "MOV " +"R1 " + ", #" + operand + "\n"
            assembly = assembly + "BL printf\n" 
        assembly = assembly + "pop {ip, lr}\n"

    # Generating assembly code if the tac is a return statement
    elif operator == "exit":
        assembly = assembly + "BL exit\n"

    # Generating the prelude for a function definition
    elif operator == "function":
        function_name = instruction[2]
        assembly = assembly + ".globl " + function_name + "\n"
        assembly = assembly + ".type "  + function_name + ", %function\n"
        assembly = assembly + function_name + ":\n"
        assembly = assembly + "PUSH {R4,LR}\n"

#    # Generating assembly code if the tac is a label for a new leader
#    elif operator == "label":
#        label = instruction[2]
#        assembly = assembly + label + ": \n"

    elif operator == "param":
        #LineNo, param, val
        val = instruction[2]
        if isnumber(val):
            assembly = assembly + "LDR R0, =#" + val + "\n"
        else:
            loc2 = getlocation(val)
            if loc2 != "mem":
                assembly = assembly + "MOV R0, " + loc2 + "\n"
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + val +  "\n" 
                assembly = assembly + "LDR " + "R0" + ", " + "[R1]" +  "\n"
        assembly = assembly + "PUSH {R0,R4}\n"

    elif operator == "args":
        val = instruction[2]
        regdest,assembly = getReg(val, line, assembly)
        assembly = assembly + "POP {R1,R4}\n"
        assembly = assembly + "POP {R0,R2}\n"
        assembly = assembly + "PUSH {R1,R4}\n"
        assembly = assembly + "MOV " + regdest + ", R0\n"
        setregister(regdest, val)
        setlocation(val, regdest)                

    # Generating assembly code if the tac is a function call
    elif operator == "call":
        #Lno., call, func_name, arg_num, ret
        # Add code to write all the variables to the memory
        # arg_num = instruction[3]
        retval = instruction[3]
        for var in varlist:
            loc = getlocation(var)
            if loc != "mem":
                assembly = assembly + "LDR " +"R0" + ", =" + var + "\n" 
                assembly = assembly + "STR " + loc + ", [R0]" + "\n"
                setlocation(var, "mem")
        label = instruction[2]
        assembly = assembly + "BL " + label + "\n"
        regdest ,assembly = getReg(retval, line, assembly)
        assembly = assembly + "MOV " + regdest + " , R0" + "\n"
        setregister(regdest, retval)
        setlocation(retval, regdest)                

    # Generating the conclude of the function
    elif operator == "return":
        #LNo, return, val
        if(len(instruction)>2):
            val = instruction[2]
            if isnumber(val):
                assembly = assembly + "LDR " + "R0, =#" + val + "\n"
            elif not isnumber(val):
                loc = getlocation(val)
                if loc != "mem":
                    assembly = assembly + "MOV " + "R0, " + loc + "\n"
                else:
                    assembly = assembly + "LDR " + "R1" + " ,=" + val + "\n"
                    assembly = assembly + "LDR R0 ,[R1]\n"
        assembly = assembly + "POP {R4,PC}\n"

    # Generating assembly code if the tac is an ifgoto statement
    elif operator == "ifgoto":
        # Add code to write all the variables to the memory
        for var in varlist:
            loc = getlocation(var)
            if loc != "mem":
                assembly = assembly + "LDR " +"R0" + ", =" + var + "\n"
                assembly = assembly + "STR " + loc + ", [R0]" + "\n"
                setlocation(var, "mem")
        operator = instruction[2]
        operand1 = instruction[3]
        operand2 = instruction[4]
        label = instruction[5]
        #check whether the operands are variables or constants
        if not isnumber(operand1) and not isnumber(operand2): #both the operands are variables
            #Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            #Get the register for comparing the operands
            #generating assembly instructions
            if loc1 != "mem" and loc2 != "mem":
                assembly = assembly + "CMP " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + "R2" + ", " + loc2 + "\n"
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 + "\n"
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n"
                assembly = assembly + "CMP " + loc1 + ", R2" + "\n"
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n"
                assembly = assembly + "LDR " + "R1" + ", [R1]" + "\n"
                assembly = assembly + "LDR " + "R2" + ", =" + operand2 + "\n"
                assembly = assembly + "LDR " + "R2" + ", [R2]" + "\n" 
                assembly = assembly + "CMP " + "R1" + ", R2" + "\n" 
        elif not isnumber(operand1) and isnumber(operand2): #only operand1 is variable
            # Get the register to store the result
            loc1 = getlocation(operand1)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand2 + "\n"
            if loc1 != "mem":
                assembly = assembly + "CMP " + loc1 + ", R0" + "\n"
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n"
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n"
                assembly = assembly + "CMP " + "R2" + ", " + "R0" + "\n"
        elif isnumber(operand1) and not isnumber(operand2): #only operand2 is variables
            #Get the location of the 1st operand
            loc2 = getlocation(operand2)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 + "\n"
            if loc2 != "mem":
                assembly = assembly + "CMP " + loc2 + ", R0" + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n"
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n"
                assembly = assembly + "CMP " + "R0" + ", " + "R2" + "\n" 
        elif isnumber(operand1) and isnumber(operand2): #none of the operandsare variables
            assembly = assembly + "LDR " + "R0" + ", =#" + operand1 + "\n" 
            assembly = assembly + "LDR " + "R1" + ", [R0]" + "\n"
            assembly = assembly + "LDR " + "R0" + ", =#" + operand2 + "\n"
            assembly = assembly + "LDR " + "R2" + ", [R0]" + "\n" 
            assembly = assembly + "CMP " + "R1" + ", R2" + "\n" 
        # Add code to write all the variables to the memory
        for var in varlist:
            loc = getlocation(var)
            if loc != "mem":
                assembly = assembly + "LDR " +"R0" + ", =" + var + "\n"
                assembly = assembly + "STR " + loc + ", [R0]" + "\n"
                setlocation(var, "mem")
        if isnumber(label):
            label = "L" + label
        if operator == "<=":
            assembly = assembly + "BLE " + label + "\n" 
        elif operator == ">=":
            assembly = assembly + "BGE " + label + "\n"
        elif operator == "==":
            assembly = assembly + "BEQ " + label + "\n"
        elif operator == "<":
            assembly = assembly + "BLT " + label + "\n"
        elif operator == ">":
            assembly = assembly + "BGT " + label + "\n" 
        elif operator == "!=":
            assembly = assembly + "BNE " + label + "\n"

    # goto statement
    elif operator == "goto":
        # Add code to write all the variables to the memory
        for var in varlist:
            loc = getlocation(var)
            if loc != "mem":
                assembly = assembly + "LDR " +"R0" + ", =" + var + "\n"
                assembly = assembly + "STR " + loc + ", [R0]" + "\n"
                setlocation(var, "mem")
        
        label = instruction[2]
        if isnumber(label):
            assembly = assembly + "B L" + label + "\n"
        else:
            assembly = assembly + "B " + label + "\n"

    elif operator == '<=':
        result = instruction[2]
        operand1 = instruction[3]
        operand2 = instruction[4]
        T = "GT"+str(relcount)
        NT = "GNT"+str(relcount)
        if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + regdest + ", =#" + str(int(int(operand1)<=int(operand2))) + "\n"
            # Update the address descriptor entry for result variable to say where it is stored no
            setregister(regdest, result)
            setlocation(result, regdest)
        elif isnumber(operand1) and not isnumber(operand2):
            #case: result = 5 < x
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + regdest + ", =#" + operand1 + "\n" 
            if loc2 != "mem":
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R0" + ", " + "=" + operand2 + "\n"
                assembly = assembly + "LDR "  + "R1" + ", [R0]"  + "\n"
                assembly = assembly + "CMP " + regdest + ", " + "R1" + "\n" 
            assembly = assembly + "BLE " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0"  + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1"  + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand2 + "\n" 
            if loc1 != "mem":
                assembly = assembly + "MOV " + regdest + ", " + loc1 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + regdest + ", [R1]" + "\n" 
            assembly = assembly + "CMP " + regdest + ", "+"R0"  + "\n" 
            assembly = assembly + "BLE " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and not isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                assembly = assembly + "CMP " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "MOV " + regdest + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + loc1 + ", R2" + "\n" 
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + "R1" + ", [R0]" + "\n" 
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R0]" + "\n" 
                assembly = assembly + "CMP " + "R1" + ", R2" + "\n" 
            # Update the register descriptor entry for regdest to say that it contains the result
            assembly = assembly + "BLE " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" +  "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            # Update the address descriptor entry for result variable to say where it is stored now
            setlocation(result, regdest)
        relcount = relcount + 1

    elif operator == '>=':
        result = instruction[2]
        operand1 = instruction[3]
        operand2 = instruction[4]
        T = "GT"+str(relcount)
        NT = "GNT"+str(relcount)
        if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + regdest + ", =#" + str(int(int(operand1)>=int(operand2))) + "\n"
            # Update the address descriptor entry for result variable to say where it is stored no
            setregister(regdest, result)
            setlocation(result, regdest)
        elif isnumber(operand1) and not isnumber(operand2):
            #case: result = 5 < x
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + regdest + ", =#" + operand1 + "\n" 
            if loc2 != "mem":
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R0" + ", " + "=" + operand2 + "\n"
                assembly = assembly + "LDR "  + "R1" + ", [R0]"  + "\n"
                assembly = assembly + "CMP " + regdest + ", " + "R1" + "\n" 
            assembly = assembly + "BGE " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0"  + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1"  + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand2 + "\n" 
            if loc1 != "mem":
                assembly = assembly + "MOV " + regdest + ", " + loc1 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + regdest + ", [R1]" + "\n" 
            assembly = assembly + "CMP " + regdest + ", "+"R0"  + "\n" 
            assembly = assembly + "BGE " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and not isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                assembly = assembly + "CMP " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "MOV " + regdest + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + loc1 + ", R2" + "\n" 
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + "R1" + ", [R0]" + "\n" 
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R0]" + "\n" 
                assembly = assembly + "CMP " + "R1" + ", R2" + "\n" 
            # Update the register descriptor entry for regdest to say that it contains the result
            assembly = assembly + "BGE " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" +  "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            # Update the address descriptor entry for result variable to say where it is stored now
            setlocation(result, regdest)
        relcount = relcount + 1

    elif operator == '==':
        result = instruction[2]
        operand1 = instruction[3]
        operand2 = instruction[4]
        T = "GT"+str(relcount)
        NT = "GNT"+str(relcount)
        if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + regdest + ", =#" + str(int(int(operand1)==int(operand2))) + "\n"
            # Update the address descriptor entry for result variable to say where it is stored no
            setregister(regdest, result)
            setlocation(result, regdest)
        elif isnumber(operand1) and not isnumber(operand2):
            #case: result = 5 < x
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + regdest + ", =#" + operand1 + "\n" 
            if loc2 != "mem":
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R0" + ", " + "=" + operand2 + "\n"
                assembly = assembly + "LDR "  + "R1" + ", [R0]"  + "\n"
                assembly = assembly + "CMP " + regdest + ", " + "R1" + "\n" 
            assembly = assembly + "BEQ " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0"  + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1"  + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand2 + "\n" 
            if loc1 != "mem":
                assembly = assembly + "MOV " + regdest + ", " + loc1 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + regdest + ", [R1]" + "\n" 
            assembly = assembly + "CMP " + regdest + ", "+"R0"  + "\n" 
            assembly = assembly + "BEQ " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and not isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                assembly = assembly + "CMP " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "MOV " + regdest + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + loc1 + ", R2" + "\n" 
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + "R1" + ", [R0]" + "\n" 
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R0]" + "\n" 
                assembly = assembly + "CMP " + "R1" + ", R2" + "\n" 
            # Update the register descriptor entry for regdest to say that it contains the result
            assembly = assembly + "BEQ " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" +  "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            # Update the address descriptor entry for result variable to say where it is stored now
            setlocation(result, regdest)
        relcount = relcount + 1

    elif operator == '!=':
        result = instruction[2]
        operand1 = instruction[3]
        operand2 = instruction[4]
        T = "GT"+str(relcount)
        NT = "GNT"+str(relcount)
        if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + regdest + ", =#" + str(int(int(operand1)!=int(operand2))) + "\n"
            # Update the address descriptor entry for result variable to say where it is stored no
            setregister(regdest, result)
            setlocation(result, regdest)
        elif isnumber(operand1) and not isnumber(operand2):
            #case: result = 5 < x
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + regdest + ", =#" + operand1 + "\n" 
            if loc2 != "mem":
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R0" + ", " + "=" + operand2 + "\n"
                assembly = assembly + "LDR "  + "R1" + ", [R0]"  + "\n"
                assembly = assembly + "CMP " + regdest + ", " + "R1" + "\n" 
            assembly = assembly + "BNE " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0"  + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1"  + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand2 + "\n" 
            if loc1 != "mem":
                assembly = assembly + "MOV " + regdest + ", " + loc1 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + regdest + ", [R1]" + "\n" 
            assembly = assembly + "CMP " + regdest + ", "+"R0"  + "\n" 
            assembly = assembly + "BNE " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and not isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                assembly = assembly + "CMP " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "MOV " + regdest + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + loc1 + ", R2" + "\n" 
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + "R1" + ", [R0]" + "\n" 
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R0]" + "\n" 
                assembly = assembly + "CMP " + "R1" + ", R2" + "\n" 
            # Update the register descriptor entry for regdest to say that it contains the result
            assembly = assembly + "BNE " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" +  "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            # Update the address descriptor entry for result variable to say where it is stored now
            setlocation(result, regdest)
        relcount = relcount + 1

    elif operator == '<':
        result = instruction[2]
        operand1 = instruction[3]
        operand2 = instruction[4]
        T = "GT"+str(relcount)
        NT = "GNT"+str(relcount)
        if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + regdest + ", =#" + str(int(int(operand1)<int(operand2))) + "\n"
            # Update the address descriptor entry for result variable to say where it is stored no
            setregister(regdest, result)
            setlocation(result, regdest)
        elif isnumber(operand1) and not isnumber(operand2):
            #case: result = 5 < x
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + regdest + ", =#" + operand1 + "\n" 
            if loc2 != "mem":
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R0" + ", " + "=" + operand2 + "\n"
                assembly = assembly + "LDR "  + "R1" + ", [R0]"  + "\n"
                assembly = assembly + "CMP " + regdest + ", " + "R1" + "\n" 
            assembly = assembly + "BLT " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0"  + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1"  + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand2 + "\n" 
            if loc1 != "mem":
                assembly = assembly + "MOV " + regdest + ", " + loc1 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + regdest + ", [R1]" + "\n" 
            assembly = assembly + "CMP " + regdest + ", "+"R0"  + "\n" 
            assembly = assembly + "BLT " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and not isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                assembly = assembly + "CMP " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "MOV " + regdest + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + loc1 + ", R2" + "\n" 
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + "R1" + ", [R0]" + "\n" 
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R0]" + "\n" 
                assembly = assembly + "CMP " + "R1" + ", R2" + "\n" 
            # Update the register descriptor entry for regdest to say that it contains the result
            assembly = assembly + "BLT " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" +  "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            # Update the address descriptor entry for result variable to say where it is stored now
            setlocation(result, regdest)
        relcount = relcount + 1

    elif operator == '>':
        result = instruction[2]
        operand1 = instruction[3]
        operand2 = instruction[4]
        T = "GT"+str(relcount)
        NT = "GNT"+str(relcount)
        if isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            assembly = assembly + "LDR " + regdest + ", =#" + str(int(int(operand1)>int(operand2))) + "\n"
            # Update the address descriptor entry for result variable to say where it is stored no
            setregister(regdest, result)
            setlocation(result, regdest)
        elif isnumber(operand1) and not isnumber(operand2):
            #case: result = 5 < x
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc2 = getlocation(operand2)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + regdest + ", =#" + operand1 + "\n" 
            if loc2 != "mem":
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            else:
                assembly = assembly + "LDR " + "R0" + ", " + "=" + operand2 + "\n"
                assembly = assembly + "LDR "  + "R1" + ", [R0]"  + "\n"
                assembly = assembly + "CMP " + regdest + ", " + "R1" + "\n" 
            assembly = assembly + "BGT " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0"  + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1"  + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            loc1 = getlocation(operand1)
            # Move the first operand to the destination register
            assembly = assembly + "LDR " + "R0" + ", =#" + operand2 + "\n" 
            if loc1 != "mem":
                assembly = assembly + "MOV " + regdest + ", " + loc1 + "\n" 
            else:
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + regdest + ", [R1]" + "\n" 
            assembly = assembly + "CMP " + regdest + ", "+"R0"  + "\n" 
            assembly = assembly + "BGT " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" + "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            setlocation(result, regdest)                
        elif not isnumber(operand1) and not isnumber(operand2):
            # Get the register to store the result
            regdest ,assembly = getReg(result, line, assembly)
            # Get the locations of the operands
            loc1 = getlocation(operand1)
            loc2 = getlocation(operand2)
            if loc1 != "mem" and loc2 != "mem":
                assembly = assembly + "CMP " + loc1 + ", " + loc2 + "\n" 
            elif loc1 == "mem" and loc2 != "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand1 + "\n" 
                assembly = assembly + "MOV " + regdest + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + regdest + ", " + loc2 + "\n" 
            elif loc1 != "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R1" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R1]" + "\n" 
                assembly = assembly + "CMP " + loc1 + ", R2" + "\n" 
            elif loc1 == "mem" and loc2 == "mem":
                assembly = assembly + "LDR " + "R0" + ", =" + operand1 + "\n" 
                assembly = assembly + "LDR " + "R1" + ", [R0]" + "\n" 
                assembly = assembly + "LDR " + "R0" + ", =" + operand2 + "\n" 
                assembly = assembly + "LDR " + "R2" + ", [R0]" + "\n" 
                assembly = assembly + "CMP " + "R1" + ", R2" + "\n" 
            # Update the register descriptor entry for regdest to say that it contains the result
            assembly = assembly + "BGT " + T + "\n"
            assembly = assembly + "MOV " + regdest + ", #0" +  "\n" 
            assembly = assembly + "B " + NT + "\n"
            assembly = assembly + T + ":" + "\n"
            assembly = assembly + "MOV " + regdest + ", #1" + "\n" 
            assembly = assembly + NT + ":" + "\n"
            setregister(regdest, result)
            # Update the address descriptor entry for result variable to say where it is stored now
            setlocation(result, regdest)
        relcount = relcount + 1

    return assembly

#######################################################################################################################################3

# Get the TAC filename
if len(sys.argv) < 2:
    print ("Provide the filename of TAC code")
    exit()
else:
    fname = str(sys.argv[1])

#Get list of instructions
tac_code = []
with open(fname,'r') as fid:
    tac_code = fid.read().strip('\n')
instr_list = tac_code.split('\n')

#Get list of variables defined
for instr in instr_list:
    rule = instr.split(', ')
    if rule[1] not in ['call','label', 'function']:
        varlist = varlist + rule
varlist = [x for x in varlist if not isnumber(x)]
varlist = list(set(varlist))
for word in tackeywords:
    if word in varlist:
        varlist.remove(word)

#List of tables required to generate efficient assembly code
#Next Use table for variables present in program for spilling registers
nextuseTable = [None for i in range(len(instr_list))]
#Table denoted address of each variable to indicate if we can acces it from register or main memory
addressDescriptor = addressDescriptor.fromkeys(varlist, "mem")

labels = {}
for i in range(len(instr_list)):
    instr = instr_list[i].split(', ')
    if instr[1]=="label":
        labels[instr[2]]=instr[0]

for key in labels:
    if key in varlist:
        varlist.remove(key)

# Get the leaders
leaders = [1,]
for i in range(len(instr_list)):
    instr_list[i] = instr_list[i].split(', ')
    if 'ifgoto' in instr_list[i] or 'goto' in instr_list[i] :
        instr_list[i][-1]=labels[instr_list[i][-1]]
        leaders.append(int(instr_list[i][-1]))
        if len(instr_list)-1>i:
            leaders.append(int(instr_list[i][0])+1)
    elif 'function' in instr_list[i] or 'label' in instr_list[i]:
        leaders.append(int(instr_list[i][0]))

leaders = list(set(leaders))
leaders.sort()

# Construct the Basic Blocks
blocks = []
i = 0
while i < len(leaders)-1:
    blocks.append(list(range(leaders[i],leaders[i+1])))
    i = i + 1
blocks.append(list(range(leaders[i],len(instr_list)+1)))

# Constructing the next use table
for block in blocks:
    revlist=block[:]
    revlist.reverse()
    symbolTable = addressDescriptor.fromkeys(varlist, ["live", None])
    for instrnumber in revlist:
        instr = instr_list[instrnumber - 1]
        operator = instr[1]
        variables = [x for x in instr if x in varlist]
        # Set the next use values here
        nextuseTable[instrnumber-1] = {var:symbolTable[var] for var in varlist}
        # Rule for mathematical operations
        if operator in mathops:
            z = instr[2]
            x = instr[3]
            y = instr[4]
            if z in variables:
                symbolTable[z] = ["dead", None]
            if x in variables:
                symbolTable[x] = ["live", instrnumber]
            if y in variables:
                symbolTable[y] = ["live", instrnumber]
        elif operator == "ifgoto":
            x = instr[3]
            y = instr[4]
            if x in variables:
                symbolTable[x] = ["live", instrnumber]
            if y in variables:
                symbolTable[y] = ["live", instrnumber]
        elif operator == "print":
            x = instr[2]
            if x in variables:
                symbolTable[x] = ["live", instrnumber]          
        elif operator == "=":
            x = instr[2]
            y = instr[3]
            if x in variables:
                symbolTable[x] = ["dead", None]
            if y in variables:
                symbolTable[y] = ["live", instrnumber]

#create sections for the ARM assembly code
#reference standard library functions
extern = ".extern exit,printf"
#store all variables as global variable initialized to 0
data_section = ".data\n"
for var in varlist:
    data_section = data_section + var + ":" + ".int 0\n"
data_section = data_section + "str: .asciz \"%d\\n\""+"\n"
#text section for code
text_section = ".text\n" + ".globl main\n" + "main:\n"
div ="unsigned_longdiv:\n"+"push {r4, lr}\n"+"mov r2, #0\n"+"mov r3, #0\n"+"mov r4, #32\n"+"b .Lloop_check1\n"+".Lloop1:\n"+"movs r0, r0, LSL #1\n"+"adc r3, r3, r3\n"+"cmp r3, r1\n"+"subhs r3, r3, r1\n"+"adc r2, r2, r2\n"+".Lloop_check1:\n"+"subs r4, r4, #1\n"+"bpl .Lloop1\n"+"pop {r4, lr}\n"+"bx lr\n"

for block in blocks:
    text_section = text_section + "L" + str(block[0]) + ":\n"
    for n in block:
        text_section = text_section + translate(instr_list[n-1])
if div_bool:
    arm_code = extern + "\n" + data_section+ "\n" + text_section +"\n"+ div 
else: 
    arm_code = extern + "\n" + data_section+ "\n" + text_section 

print (arm_code)
