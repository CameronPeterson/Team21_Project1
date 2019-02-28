# TODO: Create test input
# TODO: Adjust BREAK to match instructions....?
# TODO: Handle signed immediate values. See Page 48 of Lec5Proj1-1.pptx

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
addr = []

# Masks used in parsing machine code strings
rnMask = 0x3E0
rmMask = 0x1F0000
rdMask = 0x1F
imMask = 0x3FFC00
shmtMask = 0xFc00
addrMask = 0x1FF000
addr2Mask = 0xFFFFE0
imsftMask = 0x600000
imdataMask = 0x1FFFE0
brMask = 0x3FFFFFF
brkMask = 0x1FFFFF
twosMask = 0x80000000

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
                print(self.input_file_name)         #debugging
            elif (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
                self.output_file_name = sys.argv[i + 1]
                print(self.output_file_name)        #debugging

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

        addrBase = 96

        for instruction in self.input_file:             # instructions from file added line by line to raw_instruction[]
            raw_instruction.append(instruction[0:32])   # "\n" character is ignored

        for instruction in raw_instruction:             # first 11 bits of each instruction added to opcode[]
            opcode.append(instruction[0:11])

        for i in range(len(opcode)):                    # opcodes are evaluated as bins. if they match a known opcode,
            if int(opcode[i], base=2) == 1112:          # global lists are populated with opcodes, args, formatted instruction
                opcode_str.append("ADD")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & rmMask) >> 16)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("R" + str(arg2[i]))
            elif int(opcode[i], base=2) == 1624:
                opcode_str.append("SUB")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & rmMask) >> 16)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("R" + str(arg2[i]))
            elif int(opcode[i], base=2) == 1104:
                opcode_str.append("AND")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & rmMask) >> 16)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("R" + str(arg2[i]))
            elif int(opcode[i], base=2) == 1360:
                opcode_str.append("ORR")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & rmMask) >> 16)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("R" + str(arg2[i]))
            elif 160 <= int(opcode[i], base=2) <= 191:
                opcode_str.append("B")
                arg1.append((int(raw_instruction[i], base=2) & brMask))
                arg2.append("")
                arg3.append("")
                arg1Str.append("")
                arg2Str.append("#" + str(arg1[i]))
                arg3Str.append("")
            elif int(opcode[i], base=2) in (1160, 1161):
                opcode_str.append("ADDI")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & imMask) >> 10)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("#" + str(arg2[i]))
            elif int(opcode[i], base=2) in (1672, 1673):
                opcode_str.append("SUBI")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & imMask) >> 10)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("#" + str(arg2[i]))
            elif 1440 <= int(opcode[i], base=2) <= 1447:
                opcode_str.append("CBZ")
                arg1.append((int(raw_instruction[i], base=2) & addr2Mask) >> 5)
                arg2.append("")
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("#" + str(arg1[i]))
                arg3Str.append("")
            elif 1448 <= int(opcode[i], base=2) <= 1455:
                opcode_str.append("CBNZ")
                arg1.append((int(raw_instruction[i], base=2) & addr2Mask) >> 5)
                arg2.append("")
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("#" + str(arg1[i]))
                arg3Str.append("")
            elif 1684 <= int(opcode[i], base=2) <= 1687:
                opcode_str.append("MOVZ")
                arg1.append((int(raw_instruction[i], base=2) & imdataMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & imsftMask) >> 17)#shifted 17 instead of 21 to multiply value by 16
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append(str(arg1[i]) + ", ")
                arg3Str.append("LSL " + str(arg2[i]))
            elif 1940 <= int(opcode[i], base=2) <= 1943:
                opcode_str.append("MOVK")
                arg1.append((int(raw_instruction[i], base=2) & imdataMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & imsftMask) >> 17)#shifted 17 instead of 21 to multiply value by 16
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append(str(arg1[i]) + ", ")
                arg3Str.append("LSL " + str(arg2[i]))
            elif int(opcode[i], base=2) == 1986:
                opcode_str.append("LDUR")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & addrMask) >> 12)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("[R" + str(arg1[i]) + ", ")
                arg3Str.append("#" + str(arg2[i]) + "]")
            elif int(opcode[i], base=2) == 1984:
                opcode_str.append("STUR")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & addrMask) >> 12)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("[R" + str(arg1[i]) + ", ")
                arg3Str.append("#" + str(arg2[i]) + "]")
            elif int(opcode[i], base=2) == 1872:
                opcode_str.append("EOR")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & rmMask) >> 16)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("R" + str(arg2[i]))
            elif int(opcode[i], base=2) == 1690:
                opcode_str.append("LSR")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & shmtMask) >> 10)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("#" + str(arg2[i]))
            elif int(opcode[i], base=2) == 1691:
                opcode_str.append("LSL")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append((int(raw_instruction[i], base=2) & shmtMask) >> 10)
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("#" + str(arg2[i]))
            elif int(opcode[i], base=2) == 0:
                opcode_str.append("NOP")
                arg1.append("")
                arg2.append("")
                arg3.append("")
                arg1Str.append("")
                arg2Str.append("")
                arg3Str.append("")
            elif int(opcode[i], base=2) == 2038:
                opcode_str.append("BREAK")
                arg1.append("")
                arg2.append("")
                arg3.append("")
                arg1Str.append("")
                arg2Str.append("")
                arg3Str.append("")
                addr.append(addrBase)
                addrBase += 4
                i += 1
                while i < len(raw_instruction):
                    #yeilds 2s complement of raw_instruction[i]
                    #if raw_instruction[i][0] == "1":
                    if int(raw_instruction[i], base=2) & twosMask == twosMask:
                        opcode_str.append(str(int(raw_instruction[i], base=2) - (1 << 32)))
                    else:
                        opcode_str.append(str(int(raw_instruction[i], base=2)))
                    arg1.append("")
                    arg2.append("")
                    arg3.append("")
                    arg1Str.append("")
                    arg2Str.append("")
                    arg3Str.append("")
                    addr.append(addrBase)
                    addrBase += 4
                    i += 1
                break
            addr.append(addrBase)
            addrBase += 4

        # print_lists() prints most data from global lists
    def print_lists(self):
        outfile = open(self.output_file_name + "_dis.txt", 'w')
        for i in range(len(opcode_str)):
            if int(opcode[i], base=2) in (1104, 1112, 1360, 1624, 1690, 1691, 1872):
                outfile.write(self.bin_to_spaced_string_r(raw_instruction[i]))
            elif int(opcode[i], base=2) in (1160, 1161, 1672, 1673):
                outfile.write(self.bin_to_spaced_string_i(raw_instruction[i]))
            elif 160 <= int(opcode[i], base=2) <= 191:
                outfile.write(self.bin_to_spaced_string_b(raw_instruction[i]))
            elif 1440 <= int(opcode[i], base=2) <= 1455:
                outfile.write(self.bin_to_spaced_string_cb(raw_instruction[i]))
            elif (1684 <= int(opcode[i], base=2) <= 1687) | (1940 <= int(opcode[i], base=2) <= 1943):
                outfile.write(self.bin_to_spaced_string_im(raw_instruction[i]))
            elif int(opcode[i], base=2) in (1984, 1986):
                outfile.write(self.bin_to_spaced_string_d(raw_instruction[i]))
            elif int(opcode[i], base=2) == 2038:
                outfile.write(self.bin_to_spaced_string_brk(raw_instruction[i]) + "\t" + str(addr[i]) + "\t" + opcode_str[i] + "\n")
                continue
            else:
                outfile.write((raw_instruction[i]) + "\t" + str(addr[i]) + "\t" + opcode_str[i] + "\n")
                continue
            outfile.write("\t" + str(addr[i]) + "\t" + opcode_str[i] + "\t" + arg1Str[i] + arg2Str[i] + arg3Str[i] + "\n")

    # bin_to_spaced_string_r() formatted an r-format instruction
    def bin_to_spaced_string_r(self, bin):
        spacedStr = bin[0:11] + " " + bin[11:16] + " " + bin[16:22] + " " + bin[22:27] + " " + bin[27:32]
        return spacedStr

    def bin_to_spaced_string_i(self, bin):
        spacedStr = bin[0:10] + " " + bin[10:22] + " " + bin[22:27] + " " + bin[27:32]
        return spacedStr

    def bin_to_spaced_string_b(self, bin):
        spacedStr = bin[0:6] + " " + bin[6:32]
        return spacedStr

    def bin_to_spaced_string_cb(self, bin):
        spacedStr = bin[0:8] + " " + bin[8:27] + " " + bin[27:32]
        return spacedStr

    def bin_to_spaced_string_im(self, bin):
        spacedStr = bin[0:9] + " " + bin[9:11] + " " + bin[11:27] + " " + bin[27:32]
        return spacedStr

    def bin_to_spaced_string_d(self, bin):
        spacedStr = bin[0:11] + " " + bin[11:20] + " " + bin[20:22] + " " + bin[22:27] + " " + bin[27:32]
        return spacedStr
    def bin_to_spaced_string_brk(self, bin):
        spacedStr = bin[0:8] + " " + bin[8:11] + " " + bin[11:16] + " " + bin[16:21] + " " + bin[21:26] + " " + bin[26:32]
        return spacedStr

if __name__ == "__main__":                              # Only runs if program executed as script
    disassembler = Disassembler()
