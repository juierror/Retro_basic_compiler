# must set EOF in terminal file
# change location of terminal and grammar
# change start symbol
# code must have spacebar between all of token

# define lambda
lam = 'EMPTY'

file = open('./terminal.txt','r')
terminal = set([str(line.strip()) for line in file])
non_terminal = set()
file.close()

grammar = dict()
startSymbol = 'pgm'
haveEmpty = set()
file = open('./grammar2.txt','r')
i_gen = 1
for line in file:
    tmp = line.strip().split()
    key = tmp[0]
    non_terminal.add(key)
    tmp = tmp[2:]
    grammar[i_gen] = {key : []}
    a = []
    for i in range(len(tmp)):
        if tmp[i] == '|':
            grammar[i_gen][key] = a
            a = []
            i_gen += 1
            grammar[i_gen] = {key : []}
            continue
        if i == len(tmp)-1:
            a.append(tmp[i])
            grammar[i_gen][key] = a
            i_gen += 1
            a = []
        if tmp[i] == "EMPTY":
            haveEmpty.add(key)
        a.append(tmp[i])
#print(grammar)
#print(non_terminal)
#print(haveEmpty)
file.close()

from scanner import Scanner

# put location of input code
scan = Scanner("./input.txt")
stream = scan.getStream()
#print(stream)

# 0:line_num 1:id 2:const 3:IF 4:PRINT 5:GOTO 6:STOP 7:+ 8:- 9:< 10:= 11:EOF
parsing_table = {"pgm":[1,0,0,0,0,0,0,0,0,0,0,2],"line":[3,0,0,0,0,0,0,0,0,0,0,0],"stmt":[0,4,0,5,6,7,8,0,0,0,0,0],"asgmnt":[0,9,0,0,0,0,0,0,0,0,0,0],"exp1":[0,10,10,0,0,0,0,0,0,0,0,0],"exp2":[13,0,0,0,0,0,0,11,12,0,0,13],"term":[0,14,15,0,0,0,0,0,0,0,0,0],"if":[0,0,0,16,0,0,0,0,0,0,0,0],"cond1":[0,17,17,0,0,0,0,0,0,0,0,0],"cond2":[0,0,0,0,0,0,0,0,0,18,19,0],"print":[0,0,0,0,20,0,0,0,0,0,0,0],"goto":[0,0,0,0,0,21,0,0,0,0,0,0],"stop":[0,0,0,0,0,0,22,0,0,0,0,0] }

output = []
valid = True

from Stack import Stack

s = Stack()
s.push("EOF")
s.push(startSymbol)

index = 0

def updateOutput(type,val):
    global output
    if type == 'line_num':
        if len(output) > 0 and output[-1] == 14:
            output.append(val)
        elif len(output) > 7 and output[-8] == 13:
            output.append(14)
            output.append(val)
        else:
            output.append(10)
            output.append(val)
    elif type == 'id':
        output.append(11)
        output.append(val+1)
    elif type == 'const':
        output.append(12)
        output.append(val)
    elif type == 'IF':
        output.append(13)
        output.append(0)
    elif type == 'GOTO':
        output.append(14)
        #output.append(val)
    elif type == 'PRINT':
        output.append(15)
        output.append(0)
    elif type == 'STOP':
        output.append(16)
        output.append(0)
    elif type == '+':
        output.append(17)
        output.append(1)
    elif type == '-':
        output.append(17)
        output.append(2)
    elif type == '<':
        output.append(17)
        output.append(3)
    elif type == '=':
        output.append(17)
        output.append(4)

def match(top,type):
    return top == type or (top == "line_num" and type == "number") or (top == "const" and type == "number")

# 0:line_num 1:id 2:const 3:IF 4:PRINT 5:GOTO 6:STOP 7:+ 8:- 9:< 10:= 11:EOF
def T(A,a):
    global parsing_table
    row = parsing_table[A]
    select = 0
    if a == "number" and row[0] != 0: 
        select = row[0]
    elif a == "id":
        select = row[1]
    elif a == "number" and row[2] != 0:
        select = row[2]
    elif a == "IF":
        select = row[3]
    elif a == "PRINT":
        select = row[4]
    elif a == "GOTO":
        select = row[5]
    elif a == "STOP":
        select = row[6]
    elif a == "+":
        select = row[7]
    elif a == "-":
        select = row[8]
    elif a == "<":
        select = row[9]
    elif a == "=":
        select = row[10]
    elif a == "EOF":
        select = row[11]

    if select == 0:
        return []
    else:
        return grammar[select][A]

while index <= len(stream)-1 and not s.isEmpty():
    top = s.top()
    token = stream[index]
    type,value = token
    if top in terminal and match(top,type):
        updateOutput(top,value)
        s.pop()
        index += 1
    elif top in non_terminal:
        l = T(top,type)
        if len(l) == 0:
            valid = False
            break
        s.pop()
        for i in range(len(l)-1,-1,-1):
            if l[i] == lam:
                continue
            s.push(l[i])
    
if not s.isEmpty or index != len(stream):
    valid = False
if valid:
    #print("out")
    #print(output)
    file = open("./output.txt","w")
    for o in output:
        file.write(str(o))
        file.write(" ")
    file.close()
    print("Compile success, check output.txt file.")
else:
    print("Compile error, please check your code.")

