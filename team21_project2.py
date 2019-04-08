#TODO: Direct Simulator output to file
#TODO: Figure out what LaKomski wants us to do with data output. See block comment below.

    # When consulting the team0TEST2_out_sim.txt file to compare outputs, I've determined that either:
    #     1) I don't understand how STUR works, or
    #     2) the output of the aforementioned file is incorrect.
    # In particualr, I'm referring to "cycle: 18" in LaKomski's output. Why is it that the value in R12 to be stored in
    # [R12, #40] is reflected as being stored in memory location 345? Shouldn't it be 347?
    # Additionally, I'm guessing that he's deriving the data addresses from the name of the register where the data is
    # being stored (R12 ---> 212). However, I'm uncertain about the origins of the leading '2'. Is it arbitrary?
    # You may have also noticed that the data registers are displayed throughout execution in test9_out_sim.txt,
    # whereas in team0TEST2_out_sim.txt they are only displayed after the first STUR instruction.

#TODO: Once the above issues are resolved, change 'MEMLOC' to reflect appropriate registers in print_lists()

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

# For use in the Simulator class to hold register and data values
regs = []
regs[:32] = [0] * 32

data = []
dataExt = []
dataExt[:8] = [0] * 8

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

class Simulator:

    def __init__(self):

        self.input_file_name = 'test1_bin.txt'
        self.output_file_name = ''
        self.input_file = open(str(self.input_file_name))
        self.simulate_regs()

    def simulate_regs(self):

        cycleCount = 1
        i = 0
        while i < (len(opcode)):
            if int(opcode[i], base=2) == 1112:          #ADD
                regs[arg3[i]] = regs[arg1[i]] + regs[arg2[i]]

            elif int(opcode[i], base=2) == 1624:        #SUB
                regs[arg3[i]] = regs[arg1[i]] - regs[arg2[i]]
            
            elif int(opcode[i], base=2) == 1104:        #AND
                regs[arg3[i]] = regs[arg1[i]] & regs[arg2[i]]
            
            elif int(opcode[i], base=2) == 1360:        #ORR
                regs[arg3[i]] = regs[arg1[i]] | regs[arg2[i]]

            elif 160 <= int(opcode[i], base=2) <= 191:  #B
                self.print_lists(i, cycleCount)
                i = i + arg1[i]
                cycleCount += 1
                continue

            elif int(opcode[i], base=2) in (1160, 1161):#ADDI
                regs[arg3[i]] = regs[arg1[i]] + arg2[i]

            elif int(opcode[i], base=2) in (1672, 1673):#SUBI
                regs[arg3[i]] = regs[arg1[i]] - arg2[i]

            elif 1440 <= int(opcode[i], base=2) <= 1447:#CBZ
                if regs[arg3[i]] == 0:
                    self.print_lists(i, cycleCount)
                    i = i + arg1[i]
                    cycleCount += 1
                    continue

            elif 1448 <= int(opcode[i], base=2) <= 1455:#CBNZ
                if regs[arg3[i]] != 0:
                    self.print_lists(i, cycleCount)
                    i = i + arg1[i]
                    cycleCount += 1
                    continue
            
            elif 1684 <= int(opcode[i], base=2) <= 1687:#MOVZ
                regs[arg3[i]] = 0
                regs[arg3[i]] = arg1[i] << arg2[i]
            
            elif 1940 <= int(opcode[i], base=2) <= 1943:#MOVK
                regs[arg3[i]] = regs[arg3[i]] + (arg1[i] << arg2[i])
            
            elif int(opcode[i], base=2) == 1986:        #LDUR
                regs[arg3[i]] = data[arg2[i]-1]

            elif int(opcode[i], base=2) == 1984:        #STUR
                while len(data) < arg2[i]:
                    data.extend(dataExt)
                data[arg2[i]-1] = regs[arg3[i]]
            
            elif int(opcode[i], base=2) == 1872:        #EOR
                regs[arg3[i]] = regs[arg1[i]] ^ regs[arg2[i]]
            
            elif int(opcode[i], base=2) == 1690:        #LSR
                regs[arg3[i]] = regs[arg1[i]] >> arg2[i]

            elif int(opcode[i], base=2) == 1691:        #LSL
                regs[arg3[i]] = regs[arg1[i]] << arg2[i]

            elif int(opcode[i], base=2) == 1692:        #ASR
                regs[arg3[i]] = regs[arg1[i]] >> arg2[i]

            #elif int(opcode[i], base=2) == 0:         #NOP

            #elif int(opcode[i], base=2) == 2038:      #BREAK

            self.print_lists(i, cycleCount)
            cycleCount += 1
            i += 1

    def print_lists(self, i, cycleCount):
        print ("====================\n")
        print ("cycle:" + str(cycleCount)) + " " + str(addr[i]) + " " + str(opcode_str[i]) + " " + arg1Str[i] + arg2Str[i] + arg3Str[i]
        print ("\n")
        print ("registers:\n")
        for j in range(32):
            if j % 8 == 0:
                print "r" + str(j).zfill(2) + ":\t",
            print str(regs[j]) + "\t",
            if j % 8 == 7:
                print ("\n"),
        print ("\n"),
        print ("data:")

        for j in range(len(data)):
            if j % 8 == 0:
                print "MEMLOC:\t",
            print str(data[j]) + "\t",
            if j % 8 == 7:
                print ("\n"),


class Disassembler:
    # Constructor sets up dummy values, gets I/O files, adds and processes input, and prints disassembled code
    def __init__(self):
        self.input_file_name = 'test1_bin.txt'
        self.output_file_name = 'OUTTEST'
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
            elif (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
                self.output_file_name = sys.argv[i + 1]

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

        for instruction in self.input_file:  # instructions from file added line by line to raw_instruction[]
            raw_instruction.append(instruction[0:32])  # "\n" character is ignored

        for instruction in raw_instruction:  # first 11 bits of each instruction added to opcode[]
            opcode.append(instruction[0:11])

        for i in range(len(opcode)):  # opcodes are evaluated as bins. if they match a known opcode,
            if int(opcode[i], base=2) == 1112:  # global lists are populated with opcodes, args, formatted instruction
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
                arg1.append(self.unsigned2signed(((int(raw_instruction[i], base=2) & brMask)), 26))
                arg2.append("")
                arg3.append("")
                arg1Str.append("")
                arg2Str.append("#" + str(arg1[i]))
                arg3Str.append("")
            elif int(opcode[i], base=2) in (1160, 1161):
                opcode_str.append("ADDI")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append(self.unsigned2signed(((int(raw_instruction[i], base=2) & imMask) >> 10), 12))
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("#" + str(arg2[i]))
            elif int(opcode[i], base=2) in (1672, 1673):
                opcode_str.append("SUBI")
                arg1.append((int(raw_instruction[i], base=2) & rnMask) >> 5)
                arg2.append(self.unsigned2signed(((int(raw_instruction[i], base=2) & imMask) >> 10), 12))
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("R" + str(arg1[i]) + ", ")
                arg3Str.append("#" + str(arg2[i]))
            elif 1440 <= int(opcode[i], base=2) <= 1447:
                opcode_str.append("CBZ")
                arg1.append(self.unsigned2signed(((int(raw_instruction[i], base=2) & addr2Mask) >> 5), 19))
                arg2.append("")
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("#" + str(arg1[i]))
                arg3Str.append("")
            elif 1448 <= int(opcode[i], base=2) <= 1455:
                opcode_str.append("CBNZ")
                arg1.append(self.unsigned2signed(((int(raw_instruction[i], base=2) & addr2Mask) >> 5), 19))
                arg2.append("")
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append("#" + str(arg1[i]))
                arg3Str.append("")
            elif 1684 <= int(opcode[i], base=2) <= 1687:
                opcode_str.append("MOVZ")
                arg1.append((int(raw_instruction[i], base=2) & imdataMask) >> 5)
                arg2.append((int(raw_instruction[i],
                                 base=2) & imsftMask) >> 17)  # shifted 17 instead of 21 to multiply value by 16
                arg3.append((int(raw_instruction[i], base=2) & rdMask) >> 0)
                arg1Str.append("R" + str(arg3[i]) + ", ")
                arg2Str.append(str(arg1[i]) + ", ")
                arg3Str.append("LSL " + str(arg2[i]))
            elif 1940 <= int(opcode[i], base=2) <= 1943:
                opcode_str.append("MOVK")
                arg1.append((int(raw_instruction[i], base=2) & imdataMask) >> 5)
                arg2.append((int(raw_instruction[i],
                                 base=2) & imsftMask) >> 17)  # shifted 17 instead of 21 to multiply value by 16
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
            elif int(opcode[i], base=2) == 1692:
                opcode_str.append("ASR")
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
                    opcode_str.append(str(self.unsigned2signed(str((int(raw_instruction[i], base=2))), 32)))
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

    #returns 2s complement of bin
    def unsigned2signed(self, bin, bitNum):
        if ((twosMask >> (32 - bitNum) & (int(bin)))) == (twosMask >> (32 - bitNum)):
            return int(bin) - (1 << bitNum)
        else:
            return bin

    def print_lists(self):
        outfile = open(self.output_file_name + "_dis.txt", 'w')
        for i in range(len(opcode_str)):
            if int(opcode[i], base=2) in (1104, 1112, 1360, 1624, 1690, 1691, 1692, 1872, 0):
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
                outfile.write(
                    self.bin_to_spaced_string_brk(raw_instruction[i]) + "\t" + str(addr[i]) + "\t" + opcode_str[
                        i] + "\n")
                continue
            else:
                outfile.write((raw_instruction[i]) + "\t" + str(addr[i]) + "\t" + opcode_str[i] + "\n")
                continue
            outfile.write(
                "\t" + str(addr[i]) + "\t" + opcode_str[i] + "\t" + arg1Str[i] + arg2Str[i] + arg3Str[i] + "\n")
        outfile.write("\n")

    # returns a string in R-format
    def bin_to_spaced_string_r(self, bin):
        spacedStr = bin[0:11] + " " + bin[11:16] + " " + bin[16:22] + " " + bin[22:27] + " " + bin[27:32]
        return spacedStr

    # returns a string in I-format
    def bin_to_spaced_string_i(self, bin):
        spacedStr = bin[0:10] + " " + bin[10:22] + " " + bin[22:27] + " " + bin[27:32]
        return spacedStr

    # returns a string in B-format
    def bin_to_spaced_string_b(self, bin):
        spacedStr = bin[0:6] + " " + bin[6:32]
        return spacedStr

    # returns a string in CB-format
    def bin_to_spaced_string_cb(self, bin):
        spacedStr = bin[0:8] + " " + bin[8:27] + " " + bin[27:32]
        return spacedStr

    # returns a string in IM-format
    def bin_to_spaced_string_im(self, bin):
        spacedStr = bin[0:9] + " " + bin[9:11] + " " + bin[11:27] + " " + bin[27:32]
        return spacedStr

    # returns a string in D-format
    def bin_to_spaced_string_d(self, bin):
        spacedStr = bin[0:11] + " " + bin[11:20] + " " + bin[20:22] + " " + bin[22:27] + " " + bin[27:32]
        return spacedStr

    # returns a string formatted to resemble brake statement in example output
    def bin_to_spaced_string_brk(self, bin):
        spacedStr = bin[0:8] + " " + bin[8:11] + " " + bin[11:16] + " " + bin[16:21] + " " + bin[21:26] + " " + bin[
                                                                                                                26:32]
        return spacedStr

if __name__ == "__main__":  # Only runs if program executed as script
    disassembler = Disassembler()
    simulator = Simulator()
