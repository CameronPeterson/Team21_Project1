#TODO Add functionality for recording address of each instruction and printing address

import sys
import os

# All globals directly below are lists containing elements that are associated by an index.
# For example, opcode_str[0] holds the string version of opcode[0], which contains the binary version
raw_instruction = []
opcode = []
opcode_str = []
arg1 = []
arg2 = []
arg3 = []
arg1Str = []
arg2Str = []
arg3Str = []

# Masks used in parsing machine code strings
rnMask = 0x3E0
rmMask = 0x1F0000
rdMask = 0x1F
imMask = 0x3FFC00
shmtMask = 0xFc00
addrMask = 0x1FF000
addr2Mask = 0xFFFE0
imsftMask = 0x600000
imdataMask = 0x1FFFE0

# These globals are not yet implemented
global mem
global binMem


class Disassembler:
    # Constructor sets up dummy values, gets I/O files, adds and processes input, and prints disassembled code
    def __init__(self):
        self.input_file_name = ''
        self.output_file_name = ''
        self.get_io_params()
        self.input_file = open(str(self.input_file_name))
        self.input_to_lists()
        self.print_lists()

    # get_io_params() sets input_file_name and output_file_name to the string values immediately after the -i and -o args
    # It also prints the names of the I/O files
    def get_io_params(self):
        for i in range(len(sys.argv)):
            if (sys.argv[i] == '-i' and i < (len(sys.argv) - 1)):
                self.input_file_name = sys.argv[i + 1]
                print(self.input_file_name)
            elif (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
                self.output_file_name = sys.argv[i + 1]
                print(self.output_file_name)

    # input_to_lists() pulls data from input file and distributes data to appropriate global lists.
    # Input instructions are used to generate lists of opcodes, args, and formatted instructions
    def input_to_lists(self):
        global raw_instruction
        global opcode
        global arg1
        global arg2
        global arg3
        global arg1Str
        global arg2Str
        global arg3Str
        #TODO Last character of file is deleted if no newline at end of file. Add logic for edge case.
        for instruction in self.input_file:             # instructions from file added line by line to raw_instruction[]
            raw_instruction.append(instruction[:-1])    # Last bit is cut off to remove unecessary newline character

        for instruction in raw_instruction:             # first 11 bits of each instruction added to opcode[]
            opcode.append(instruction[0:11])

        for i in range(len(opcode)):                    # opcodes are evaluated as bins. if they match a known opcode,
            if int(opcode[i], base=2) == 1112:          # global lists are populated with opcodes, args, formatted instruction
                opcode_str.append("ADD")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & rmMask) >> 16)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append(", R" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))
            elif int(opcode[i], base=2) == 1624:
                opcode_str.append("SUB")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & rmMask) >> 16)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append(", R" + str(arg3[i]))
                arg2Str.append(", R" + str(arg1[i]))
                arg3Str.append(", R" + str(arg2[i]))
    
    # print_lists() prints most data from global lists
    def print_lists(self):
        for i in range(len(opcode_str)):
            print(self.bin_to_spaced_string_r(raw_instruction[i]) + ' ' + opcode_str[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])
            
    # bin_to_spaced_string_r() formatted an r-format instruction
    def bin_to_spaced_string_r(self, bin):
        spacedStr = bin[0:11] + " " + bin[11:16] + " " + bin[16:23] + " " + bin[23:28] + " " + bin[28:33]
        return spacedStr

    
if __name__ == "__main__":                              # Only runs if program executed as script
    disassembler = Disassembler()
