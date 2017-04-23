#!/usr/bin/env python

import sys, re

asmFile, binFile = sys.argv[1], sys.argv[2]

BIN16 = "016b"
BIN3 = "03b"

PS = {
    "@SP": "0000000000000000",
    "@LCL": "0000000000000001",
    "@ARG": "0000000000000010",
    "@THIS": "0000000000000011",
    "@THAT": "0000000000000100",
    "@R0": "0000000000000000",
    "@R1": "0000000000000001",
    "@R2": "0000000000000010",
    "@R3": "0000000000000011",
    "@R4": "0000000000000100",
    "@R5": "0000000000000101",
    "@R6": "0000000000000110",
    "@R7": "0000000000000111",
    "@R8": "0000000000001000",
    "@R9": "0000000000001001",
    "@R10": "0000000000001010",
    "@R11": "0000000000001011",
    "@R12": "0000000000001100",
    "@R13": "0000000000001101",
    "@R14": "0000000000001110",
    "@R15": "0000000000001111",
    "@SCREEN": "0100000000000000",
    "@KBD": "0110000000000000"
}
DC = ['', 'M', 'D', 'MD', 'A', 'AM', 'AD', 'AMD']
JC = ['', 'JGT', 'JEQ', 'JGE', 'JLT', 'JNE', 'JLE', 'JMP']
CC = {
    '0': '0101010',
    '1': '0111111',
    '-1': '0111010',
    'D': '0001100',
    'A': '0110000',
    '!D': '0001101',
    '!A': '0110001',
    '-D': '0001111',
    '-A': '0110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'D+A': '0000010',
    'D-A': '0010011',
    'A-D': '0000111',
    'D&A': '0000000',
    'D|A': '0010101',
    'M': '1110000',
    '!M': '1110001',
    '-M': '1110011',
    'M+1': '1110111',
    'M-1': '1110010',
    'D+M': '1000010',
    'D-M': '1010011',
    'M-D': '1000111',
    'D&M': '1000000',
    'D|M': '1010101'
}

# parsing instructions from file, clearing them from comments, spaces, whitespaces and newlines
instruction = []
tmp = ''
with open(asmFile, 'r') as asmFC:
    for line in asmFC:
        for c in line:
            if c == ' ':
                continue
            if c == '\r' and line[line.index(c) + 1] == '\n' and len(line) == (line.index(c) + 2):
                break
            elif c == '/' and line[line.index(c) + 1] == '/':
                break
            else:
                tmp = tmp + c
        instruction.append(tmp)
        tmp = ''
instruction = filter(None, instruction)

LABELS_TABLE = {}
liter = 0
for inst in instruction:
    if inst[0] == '(':
        if inst not in LABELS_TABLE:
            LABELS_TABLE.update({inst : liter})
    liter += 1

VARS_TABLE = {}
viter = 15
for inst in instruction:
    if inst[0] == '@' and not inst[1:].isdigit() and inst not in PS and '(' + inst[1:] + ')' not in LABELS_TABLE:
        if inst not in VARS_TABLE:
            VARS_TABLE.update({inst : viter})
    viter += 1

# process C-instruction
def C(val):
    # C - instruction:
    # dest=comp;jump
    # Dest or jump fields may be empty.
    # If dest is empty, the = is omitted
    # If jump is empty, the ; is omitted
    # 1 1 1 a c1 c2 c3 c4 c5 c6 d1 d2 d3 j1 j2 j3

    cidx = 0
    jidx = None

    # Dest
    if '=' in val:
        cidx = val.index('=')
        DCPART = format(DC.index(val.rsplit('=', 1)[0]), BIN3)
        # DCPART = val.rsplit('=', 1)[0]
    else:
        DCPART = format(DC.index(''), BIN3)

    # Jump
    if ';' in val:
        jidx = val.index(';')
        JCPART = format(JC.index(val.rsplit(';', 1)[1]), BIN3)
    else:
        JCPART = format(JC.index(''), BIN3)

    # Comp
    if cidx > 0:
        CPART = val[(cidx + 1):jidx]
    else:
        CPART = val[(cidx):jidx]
    if CPART in CC:
        CPART = CC.get(CPART)
    else:
        CPART = CC.get(val[(cidx + 1):(cidx + 2)])
        if not CPART:
            CPART = CC.get('0')

    CBIN = '111' + CPART + DCPART + JCPART
    return CBIN


# fixing broken references after label deletion
for i in instruction:
    if i in LABELS_TABLE:
        for label, sp in LABELS_TABLE.items():
            if LABELS_TABLE[label] > LABELS_TABLE[i]:
                LABELS_TABLE[label] = sp - 1

# replacing A-instruction with binary and send C to process
def proc(val,idx):
    Aflag = False
    bininstruction = ''

    if val in PS:
        Aflag = True
        bininstruction = PS[val]

    if val in LABELS_TABLE:
        Aflag = True
        bininstruction = None

    # if @REFERENCE in LABELS_TABLE
    if '(' + val[1:] + ')' in LABELS_TABLE:
        print str(idx)+": "+val + " removing reference to " + '(' + val[1:] + ')' + " from instructions " + str(LABELS_TABLE['(' + val[1:] + ')'])
        Aflag = True
        bininstruction = format(LABELS_TABLE['(' + val[1:] + ')'], BIN16)

    if val in VARS_TABLE: # if @variable in VARS_TABLE
        print str(idx)+": "+val + " replacing variable with " + str(VARS_TABLE[val])
        Aflag = True
        bininstruction = format(VARS_TABLE[val], BIN16)

    # if value like @14 just replace it with binary representation
    if val[1:].isdigit():
        Aflag = True
        bininstruction = format(int(val[1:]), BIN16)

    # if not A
    if not Aflag:
        bininstruction = C(val)

    Aflag = False
    return bininstruction

f = open(binFile, "w")

for idx, val in enumerate(instruction):
    if proc(val, idx):
        f.write(proc(val, idx) + '\r\n')
f.close()

