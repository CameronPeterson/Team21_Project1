import sys
import os

raw_instruction = []
opcode = []
opcode_str = []

# all below globals are not implemented yet
global arg1
global arg2
global arg3
global arg1Str
global arg2Str
global arg3Str
global mem
global binMem

class Disassembler:
    def __init__(self):
        self.input_file_name = ''
        self.output_file_name = ''
        self.get_io_params()
        self.input_file = open(str(self.input_file_name))
        self.input_to_lists()

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
        for instruction in self.input_file:         # instructions from file added line by line to raw_instruction[]
            raw_instruction.append(instruction)

        for instruction in raw_instruction:         # first 11 bits of instruction added to opcode[]
            opcode.append(instruction[0:11])

        for op in opcode:                           # opcodes are evaluated as bins if they match a known opcode,
            if int(op, base=2) == 1112:             # the opcode name is added to opcode_str[]
                opcode_str.append("ADD")
            elif int(op, base=2) == 1624:
                opcode_str.append("SUB")

    def process_opcode_str(self):
        return


if __name__ == "__main__":
    disassembler = Disassembler()