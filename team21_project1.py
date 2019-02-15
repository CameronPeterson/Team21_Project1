
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
mem = []

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
            if sys.argv[i] == '-i' and i < (len(sys.argv) - 1):
                self.input_file_name = sys.argv[i + 1]
                print(self.input_file_name)
            elif sys.argv[i] == '-o' and i < (len(sys.argv) - 1):
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

        mem_base = 96

        for instruction in self.input_file:             # instructions from file added line by line to raw_instruction[]
            raw_instruction.append(instruction[0:32])   # "\n" character is ignored

        for instruction in raw_instruction:             # first 11 bits of each instruction added to opcode[]
            opcode.append(instruction[0:11])

        for i in range(len(opcode)):                    # opcodes are evaluated as bins. if they match a known opcode,
            # R-format instructions
            if int(opcode[i], base=2) == 1112:
                opcode_str.append("ADD")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & rmMask) >> 16)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("R" + str(arg2[i]))
                mem.append(mem_base)
                mem_base += 4
            elif int(opcode[i], base=2) == 1624:
                opcode_str.append("SUB")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & rmMask) >> 16)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("R" + str(arg2[i]))
                mem.append(mem_base)
                mem_base += 4
            elif int(opcode[i], base=2) == 1691:
                opcode_str.append("LSL")
                # TODO
            elif int(opcode[i], base=2) == 1690:
                opcode_str.append("LSR")
                # TODO
            elif int(opcode[i], base=2) == 1104:
                opcode_str.append("AND")
                # TODO
            elif int(opcode[i], base=2) == 1360:
                opcode_str.append("ORR")
                # TODO
            elif int(opcode[i], base=2) == 1616:
                opcode_str.append("EOR")
                # TODO

            # I-format instructions
            elif 1160 <= int(opcode[i], base=2) <= 1161:
                opcode_str.append("ADDI")
                # TODO
            elif 1672 <= int(opcode[i], base=2) <= 1673:
                opcode_str.append("SUBI")
                # TODO

            # D-format instructions
            elif int(opcode[i], base=2) == 1986:
                opcode_str.append("LDUR")
                # TODO
            elif int(opcode[i], base=2) == 1984:
                opcode_str.append("STUR")
                # TODO

            # CB-format instructions
            elif 1440 <= int(opcode[i], base=2) <= 1447:
                opcode_str.append("CBZ")
                # TODO
            elif 1448 <= int(opcode[i], base=2) <= 1455:
                opcode_str.append("CBNZ")
                # TODO

            # IM-format instructions
            elif 1684 <= int(opcode[i], base=2) <= 1687:
                opcode_str.append("MOVZ")
                # TODO
            elif 1940 <= int(opcode[i], base=2) <= 1943:
                opcode_str.append("MOVK")
                # TODO

            # B-format instructions
            elif 160 <= int(opcode[i], base=2) <= 191:
                opcode_str.append("B")
                # TODO
            elif 1448 <= int(opcode[i], base=2) <= 1455:
                opcode_str.append("CBNZ")
                # TODO

            # NOP instruction
            elif int(opcode[i], base=2) == 0:
                opcode_str.append("NOP")
                # TODO (confirm that a NOP is == 0 in machine code before writing the rest of this)

    # print_lists() prints most data from global lists
    def print_lists(self):
        for i in range(len(opcode_str)):
            print(self.bin_to_spaced_string_r(raw_instruction[i]) + '\t' + str(mem[i]) + '\t' + opcode_str[i]
                  + '\t' + arg1Str[i] + arg2Str[i] + arg3Str[i])
            
    # bin_to_spaced_string_r() formats a 32-bit binary string as an r-format instruction
    def bin_to_spaced_string_r(self, unformatted_str):
        spacedStr = unformatted_str[0:11] + " " + unformatted_str[11:16] + " " + unformatted_str[16:23]+" " +\
                    unformatted_str[23:28] + " " + unformatted_str[28:33]
        return spacedStr

    def bin_to_spaced_string_i(self, unformatted_str):
        # TODO generate i-type formatted binary string
        return

    def bin_to_spaced_string_d(self, unformatted_str):
        # TODO generate d-type formatted binary string
        return

    def bin_to_spaced_string_im(self, unformatted_str):
        # TODO
        return

    def bin_to_spaced_string_b(self, unformatted_str):
        # TODO
        return


if __name__ == "__main__":                              # Only runs if program executed as script
    disassembler = Disassembler()
