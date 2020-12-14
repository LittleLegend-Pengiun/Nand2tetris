#!/usr/bin/python
import os, sys



# these three dictionaries store the translations of the 3 parts
# of a c-instruction
# C-instruction format: dest = comp; jump
comp = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
  }


dest = {
    "null": "000",
    "M": "001",
    "D": "010",
    "A": "100",
    "MD": "011",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
  }


jump = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
  }


# table of symbols used in assembly code, initialized to include
# standard ones
table = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}
# adding symbols from R0 to R16
for i in range(0,16):
  label = "R" + str(i)
  table[label] = i

table1 = table

#pre definition of global variables
varCursor = 0
root = "" 

def space_del(line):
  # removes whitespace and comments; returns line without a closing \n

  char = line[0]
  # if there is endline or newline character
  # turn into 
  if char == "\n" or char == "/":
    return ""
  # if the 1st character is whitespace
  # check the 2nd one recursively
  elif char == " ": 
    return space_del(line[1:])
  # if there is no white space on the first character, 
  # add it to char recursively
  else: 
    return char + space_del(line[1:])


def c_standize(line):
  # c_standizes c-instructions by adding null dest & jump fields
  # if they're unspecified
  # i.e: M = M + 1 -> M = M + 1; null
  #      D; JMP -> null = D; JMP
  # take the whole line except the last character ("")
  line = line[:-1] 
  if not ";" in line:
    line = line + ";null"
  if not "=" in line:
    line = "null=" + line
  return line


def addVariable(label):
  # allocates a memory location for new variables

  global varCursor
  table[label] = varCursor
  varCursor += 1
  return table[label]


def a_trans(line):
  # translates a symbolic a-instruction into an int (if necessary)
  # then translates that into a binary machine instruction

  # check if the instruction is right
  # isalpha() is true if there is at leat 1 char and all the char is 
  # alphabet (chu cai)
  # i.e: @CHECK
  if line[1].isalpha(): 
  # ignore the 1st char (@) and the last char ("")
    label = line[1:-1]
  # get the label from the table
  # if it not exist, return -1
    dec_val = table.get(label, -1)
  # if the value is -1, assign the new label to table
    if dec_val == -1:
      dec_val = addVariable(label)
    # the normal A-instruction: i.e: @69
  else:
    dec_val = int(line[1:]) #assign the value 
    # trans to a 16-bit binary number
  bin_val = bin(dec_val)[2:].zfill(16) 
  return bin_val
    

def c_trans(line):
# splits a c-instruction into its components & translates them

  line = c_standize(line)
  # take the dest of the instruction
  temp = line.split("=")
  destCode = dest.get(temp[0], "destFAIL")
  temp = temp[1].split(";")
  # take the comp and jump
  compCode = comp.get(temp[0], "compFAIL")
  jumpCode = jump.get(temp[1], "jumpFAIL")
  # return an aray con tain comp, dest, jump
  return compCode, destCode, jumpCode


def translate(line):
  # distinguishes a- and c-instructions, calls appropriate function
  # to translate each

  if line[0] == "@":
    return a_trans(line)
  else:
    codes = c_trans(line)
    return "111" + codes[0] + codes[1] + codes[2]


def labeling():
# searches file for jump labels and enters them into the symbol table
# also delete comments & empty lines

  infile = open(root + ".asm") #open the file
  outfile = open(root + ".tmp", "w") #create a temp file
  lineNumber = 0
  for line in infile:
    hack_ins = space_del(line)
    if hack_ins != "":
  # if there is a label, skip the "(" ")" and add the label to the
  # symbol table
      if hack_ins[0] == "(":
        label = hack_ins[1:-1]
        table[label] = lineNumber
        hack_ins = ""
  # else just copy the instruction again
      else:
        lineNumber += 1
        outfile.write(hack_ins + "\n")

  infile.close()
  outfile.close()


def to_binary():
# takes file space_delped of labels and translates it into .hack

  infile = open(root + ".tmp")
  outfile = open(root + ".hack", "w")

  for line in infile:
    bin_ins = translate(line) #translating to machine language
    outfile.write(bin_ins + "\n") #write it down to hack file

  infile.close()
  outfile.close()
  os.remove(root + ".tmp") #delete the temp file

def program():  
  global varCursor
  varCursor = 16  # next available memory location for variables
  # name of file to be translated
  global root
  root = input("Enter the name of the asm file: ")     
  name = root.split('.')
  root = name[0]
  global table
  table = table1
  # actual translating is just calls to these two functions
  labeling()
  to_binary()

# Recursively run the program again 
def choice():
  ask = input("Do you want to continue (y/n): ")
  if ask == "y":
    program()
    choice()
  elif ask == "n":
    exit()
  else:
    choice()

# actual program is just calls to these two functions
program()
choice()