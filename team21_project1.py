import sys
import os

raw_instruction = []
opcode = []
opcode_str = []
arg1 = []
arg2 = []
arg3 = []
arg1Str = []
arg2Str = []
arg3Str = []

# all below globals are not implemented yet

global mem
global binMem

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

class Disassembler:
    def __init__(self):
        self.input_file_name = ''
        self.output_file_name = ''
        self.get_io_params()
        self.input_file = open(str(self.input_file_name))
        self.input_to_lists()
        self.print_lists()

    # get_io_params() gets the strings after the -i and -o params and sets them to
    # input_file_name and output_file_name
    def get_io_params(self):
        for i in range(len(sys.argv)):
            if (sys.argv[i] == '-i' and i < (len(sys.argv) - 1)):
                self.input_file_name = sys.argv[i + 1]
                print(self.input_file_name)
            elif (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
                self.output_file_name = sys.argv[i + 1]
                print(self.output_file_name)

    # input_to_lists appends each line as an element to list opcode_str
    # opcodes are pulled from each line and added to their own list
    # TODO switch to bit masking instead of string manipulation
    def input_to_lists(self):
        global raw_instruction
        global opcode
        global arg1
        global arg2
        global arg3
        global arg1Str
        global arg2Str
        global arg3Str
        for instruction in self.input_file:             # instructions from file added line by line to raw_instruction[]
            raw_instruction.append(instruction[:-1])    # Last bit is cut off to remove unecessary newline character

        for instruction in raw_instruction:             # first 11 bits of instruction added to opcode[]
            opcode.append(instruction[0:11])

        for i in range(len(opcode)):                    # opcodes are evaluated as bins. if they match a known opcode,
            if int(opcode[i], base=2) == 1112:          # the opcode name is added to opcode_str[]
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

    def print_lists(self):
        for i in range(len(opcode_str)):
            print(self.bin_to_spaced_string_r(raw_instruction[i]) + ' ' + opcode_str[i] + arg1Str[i] + arg2Str[i] + arg3Str[i])

    def bin_to_spaced_string_r(self, bin):
        spacedStr = bin[0:11] + " " + bin[11:16] + " " + bin[16:23] + " " + bin[23:28] + " " + bin[28:33]
        return spacedStr



if __name__ == "__main__":
    disassembler = Disassembler()