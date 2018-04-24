import ply.lex as lex
import sys
import os

def get_next_element(my_itr):
    try:
        return my_itr.next()
    except StopIteration:
        return None

fil = open("output.txt",'r')
infile = iter(fil.read().split())
outfile = open("for_tree.txt",'w')

word = get_next_element(infile)
while(word):
    if word == "Error":
        outfile.write("[Error -> Error]\n")
        continue
    if word == "Reduce":
        word = get_next_element(infile)
        if word == "rule":
            while(True):
                word = get_next_element(infile)
                outfile.write(word)
                outfile.write(" ")
                if word[len(word)-1] == ']':
                    outfile.write("\n")
                    if word[0:len(word)-1] == "IDENTIFIER":
                        word = get_next_element(infile)
                        word = get_next_element(infile)
                        ch1 = word[1]
                        if ch1=="\'":
                            outfile.write("_[IDENTIFIER -> ")
                            word = word[2:len(word)-2]
                            outfile.write(word+"]\n")
                        break
                    if word[0:len(word)-1] == "INTCONST":
                        ch2 = ""
                        word = get_next_element(infile)
                        word = get_next_element(infile)
                        ch2 = word[1]
                        if ch2=="\'":
                            outfile.write("_[INTCONST -> ")
                            word = word[2:len(word)-2]
                            outfile.write(word+"]\n")
                        break
                    break
    word = get_next_element(infile)

fil.close()
outfile.close()

fil = open("for_tree.txt",'r')
infile = iter(fil.read().split())

outfile = open("parser.txt",'w')

a = []
A = []
count = 0
Str =""
i = 0
line_no = 1
word = get_next_element(infile)
while(word!=None):
    length = len(word)
    if word[length - 1] == ']':
        word = word[0:length]
        Str = Str +" "+ word
        a.append(Str)
        i += 1
        word = get_next_element(infile)
        continue
    if word[0] == '[':
        word = word[1:length]
        Str = word
        word = get_next_element(infile)
        continue
    if word[0] == '_':
        word = word[2:length]
        Str = word
        count+=1
        A.append(i)
        word = get_next_element(infile)
        continue
    else:
        Str += " " + word
        word = get_next_element(infile)
fil.close()



line_no = A.pop()
for j in xrange(i-1,-1,-1):
    if(j==line_no) :
        temp = a[j]
        a[j] = a[j-1]
        a[j-1] = temp
        if A:
            line_no = A.pop()
yes = 0
for j in xrange(i-1,-1,-1):
    outfile.write(a[j]+"\n")
    if a[j] == "Error -> Error]":
        yes = 1
        break

outfile.close()

fil = open("parser.txt",'r')
infile = iter(fil.read().split())
outfile = open("out.txt",'w')
out_html = open("right_derivation.html",'w')
out_html.write("<!DOCTYPE html>\n")
out_html.write("<html>\n")
out_html.write("<body>\n")
out_html.write("<body bgcolor=\"#000000\">\n")
out_html.write("<center>\n")
out_html.write("<h1><font face = \"Segoe Keycaps\" style=\"color:#FF3D1D;\"> RIGHT DERIVATION OF THE PROGRAM</font><h1>\n")

colour = []
previous_line = []
pre =  "compilation_unit"
outfile.write(pre+" ]\n")
previous_line.append(pre)
n = 1
l = 1
catch=0
word = get_next_element(infile)
while(word!=None) :
    for i in xrange(n-1,-1,-1):
        if word == previous_line[i]:
            catch = i
            colour.append(catch)
            break
    l+=1
    new_line = []
    count = 0
    for j in xrange(0,n,1):
        if not j==catch:
            new_line.append(previous_line[j])
            outfile.write(str(previous_line[j])+" ")
            count+=1
        else:
            while(word!=None):
                word = get_next_element(infile)
                if word == "->":
                    continue
                if word[len(word)-1]==']':
                    new_line.append(word[0:len(word)-1])
                    outfile.write(word[0:len(word)-1]+" ")
                    count+=1
                    break
                else:
                    new_line.append(word)
                    outfile.write(str(word)+" ")
                    count+=1
    n = count
    outfile.write("]\n")
    previous_line = new_line
    word = get_next_element(infile)
fil.close()
outfile.close()

fil = open("out.txt",'r')
infile = iter(fil.read().split())
i = 0
word = get_next_element(infile)
while(word!=None):
    if colour[i%len(colour)] == 0:
        out_html.write("<font size = \"2\" face = \"DotumChe\"")
        out_html.write("style=\"color:#9E4CCC;\">")
        out_html.write(str(word)+"&nbsp")
        out_html.write("</font>")
        while(word!=None):
            word = get_next_element(infile)
            if word == "]":
                out_html.write("<br>\n")
                break
            else:
                out_html.write("<font size = \"2\" face = \"DotumChe\"")
                out_html.write("style=\"color:#33FF55;\">")
                out_html.write(str(word)+"&nbsp")
                out_html.write("</font>")
        i+=1
        word = get_next_element(infile)
        continue
    else:
        toggle = 0
        while(word!=None):
            if not toggle==colour[i%len(colour)]:
                if word=="]":
                    out_html.write("<br>\n")
                    break
                else:
                    out_html.write("<font size = \"2\" face = \"DotumChe\"")
                    out_html.write("style=\"color:#33FF55;\">")
                    out_html.write(str(word)+"&nbsp")
                    out_html.write("</font>")
                toggle+=1
                word = get_next_element(infile)
                continue
            else:
                if word=="]":
                    out_html.write("<br>\n")
                    break
                else:
                    out_html.write("<font size = \"2\" face = \"DotumChe\"")
                    out_html.write("style=\"color:#9E4CCC;\">")
                    out_html.write(str(word)+"&nbsp")
                    out_html.write("</font>")
                toggle+=1
                word = get_next_element(infile)
        i+=1
    word = get_next_element(infile)

if yes:
    Fil = open("errors.txt",'r')
    File = iter(Fil.read().split())
    out_html.write("<font size = \"4\" face = \"DotumChe\"")
    out_html.write("style=\"color:red;\">")
    wor = get_next_element(File)
    while(wor!=None):
        out_html.write(str(wor)+"&nbsp")
        wor = get_next_element(File)

    out_html.write("</font>\n")
    Fil.close()

out_html.write("</center>\n")
out_html.write("</body>")
fil.close()
out_html.close()
print("The html file has been created in right_derivation.html")
