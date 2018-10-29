# must set EOF in terminal file
# change location of terminal and grammar
# change start symbol

# define lambda
lam = 'EMPTY'

###################################################################
# generate terminal ###############################################
###################################################################

file = open('./terminal.txt','r')
terminal = set([str(line.strip()) for line in file])
non_terminal = set()
file.close()

###################################################################
# generate grammar ################################################
###################################################################

grammar = dict()
startSymbol = 'pgm'
file = open('./grammar.txt','r')
for line in file:
    tmp = line.strip().split()
    key = tmp[0]
    non_terminal.add(key)
    grammar[key] = []
    tmp = tmp[2:]
    a = []
    for i in range(len(tmp)):
        if tmp[i] == '|':
            grammar[key].append(a)
            a = []
            continue
        if i == len(tmp)-1:
            a.append(tmp[i])
            grammar[key].append(a)
            a = []
        a.append(tmp[i])
#print(grammar)
#print(non_terminal)
file.close()

#####################################################################
# find first set ####################################################
#####################################################################

#print("find first set")
firstSet = dict()

def first_set(c,grammar):
    global firstSet
    # if c is terminal firstSet(terminal) = terminal or c is empty string
    if c in terminal or c == lam:
        return set([c])
    # if c already in firstSet return it
    if c in firstSet:
        return firstSet[c]
    # if c is first seen create empty set 
    if c not in firstSet:
        firstSet[c] = set()
    for g in grammar[c]:
        i = 0
        while i < len(g):
            term = g[i]
            toUnion = first_set(term,grammar)
            firstSet[c] = firstSet[c].union(toUnion.difference(set([lam])))
            if lam in toUnion:
                i += 1
            else:
                break
        if i == len(g):
            firstSet[c] = firstSet[c].union(set([lam]))
    return firstSet[c]


for a in non_terminal:
    first_set(a,grammar)

#print(firstSet)

#####################################################################
# find follow set ###################################################
#####################################################################

#print("find follow set")
followSet = dict()

# init followSet followSet(startSymbol) = EOF other is empty set
for nt in non_terminal:
    if nt == startSymbol:
        followSet[nt] = set(['EOF'])
        continue
    followSet[nt] = set()

change = True
# while there are update
while change:
    change = False
    for g in non_terminal:
        list_g = grammar[g]
        # each l is each RHS term in grammar
        for l in list_g:
            for i in range(len(l)-1):
                # A -> NB ,firstSet(B) is in followSet(N)
                if (l[i] in non_terminal) and (l[i+1] in non_terminal):
                    tmp = followSet[l[i]].copy()
                    followSet[l[i]] = followSet[l[i]].union(firstSet[l[i+1]].difference(set([lam])))
                    # check change
                    if tmp != followSet[l[i]]:
                        change = True
                # A -> Nx ,x is in followSet(N)
                elif (l[i] in non_terminal) and (l[i+1] in terminal):
                    tmp = followSet[l[i]].copy()
                    followSet[l[i]] = followSet[l[i]].union(set([l[i+1]]))
                    # check change
                    if tmp != followSet[l[i]]:
                        change = True
            # init j point to last of list l
            j = len(l)-1
            while j > 0:
                # B -> XNB and lamda is in firstSet(B)
                if l[j] == g and (lam in firstSet[l[j]]):
                    j -= 1
                # A -> XNB and lamda is in firstSet(B), followSet(A) is in followSet(B)
                elif (l[j] in non_terminal) and (lam in firstSet[l[j]]):
                    tmp = followSet[l[j]].copy()
                    followSet[l[j]] = followSet[l[j]].union(followSet[g])
                    # check change
                    if tmp != followSet[l[j]]:
                        change = True
                    j -= 1
                # A -> XN, followSet(A) is in followSet(N)
                elif l[j] in non_terminal:
                    tmp = followSet[l[j]].copy()
                    followSet[l[j]] = followSet[l[j]].union(followSet[g])
                    # check change
                    if tmp != followSet[l[j]]:
                        change = True
                    break
                # A -> Bx
                elif l[j] in terminal:
                    break
#print(followSet)

#####################################################################
# use scanner and factorize grammar #################################
#####################################################################
#print("use scanner")
from scanner import Scanner

# put location of input code
scan = Scanner("./input.txt")
stream = scan.getStream()

list_of_grammar = []
haveEmpty = set()

for key in grammar:
    tmp_g = grammar[key]
    for l in tmp_g:
        list_of_grammar.append({key : l})
        if lam in l:
            haveEmpty.add(key)
#print(stream)


#####################################################################
# parsing ###########################################################
#####################################################################

from Stack import Stack

s = Stack()
s.push("EOF")
s.push(startSymbol)

# pointer in stream
pointer = 0
# output B-code
output = []
valid = True

def fs(c):
    if c in firstSet:
        return firstSet[c]
    if c in terminal:
        return set([c])

def isInFirstSet(token_type,top):
    return token_type in fs(top) or (token_type == 'number' and 'line_num' in fs(top)) or (token_type == 'number' and 'const' in fs(top))

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

while pointer < len(stream):
    if s.isEmpty():
        break
    top = s.top()
    current_token = stream[pointer]
    token_type = current_token[0]
    token_val = current_token[1]
    #print(top,token_type,token_val)
    # token_type is in firstSet[top]
    if isInFirstSet(token_type,top):
        grammar_can_use = []
        for c in list_of_grammar:
            if top in c:
                grammar_can_use.append(c[top])
        #print("grammar can use "+str(grammar_can_use))
        choose = False
        for g in grammar_can_use:
            if isInFirstSet(token_type,g[0]):
                if top == 'exp' and stream[pointer+1][0] == '+':
                    if g[1] != '+':
                        continue
                if top == 'exp' and stream[pointer+1][0] == '-':
                    if g[1] != '-':
                        continue
                if top == 'cond' and stream[pointer+1][0] == '<':
                    if g[1] != '<':
                        continue
                if top == 'cond' and stream[pointer+1][0] == '=':
                    if g[1] != '=':
                        continue
                if top == 'asgmnt' and stream[pointer+3][0] not in ['+','-'] and g[2] == 'exp':
                    continue

                #print("grammar choose "+str(g))
                choose = True
                s.pop()
                for i in range(1,len(g)+1):
                    s.push(g[len(g)-i])
                break
        #print(token_type,top)
        if (token_type == 'number' and top == 'const') or (token_type == 'number' and top == 'line_num') or (token_type == top):
            choose = True
        #print(choose)

        if choose == False:
            valid = False
            break
    else:
        valid = False

    if not valid:
        break
    # case match token
    if top == token_type:
        pointer += 1
        updateOutput(top,token_val)
        s.pop()
    elif top == 'line_num' and token_type == 'number':
        pointer += 1
        updateOutput('line_num',token_val)
        s.pop()
    elif top == 'const' and token_type == 'number':
        pointer += 1
        updateOutput('const',token_val)
        s.pop()
    #print(output)

    # case not valid
    if (top == 'EOF' and token_type != 'EOF') or (top in terminal and ((token_type == 'number' and top not in ['line_num','const']) or (token_type != 'number' and top != token_type))):
        valid = False
        break

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
