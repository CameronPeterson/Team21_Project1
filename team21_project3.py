import sys
from datetime import datetime
from Queue import Queue
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
dataAddr = []

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

PreALUQueue = Queue(maxsize=2)
PreMEMQueue = Queue(maxsize=2)
PreIssueBuffer = Queue(maxsize=4)
PostALUBuffer = None
PostMEMBuffer = None

# Cache components
hash = {}
item_list = []

cache = None
totalCycles = len(opcode) + 4
cycleNum = 1
instQueue = Queue(maxsize=len(opcode))

GenIter = 0




def simulate_regs(inst):
    opcode = inst.opcode
    arg1 = inst.arg1
    arg2 = inst.arg2
    arg3 = inst.arg3

    if int(opcode, base=2) == 1112:  # ADD
        regs[arg3] = regs[arg1] + regs[arg2]

    elif int(opcode, base=2) == 1624:  # SUB
        regs[arg3] = regs[arg1] - regs[arg2]

    elif int(opcode, base=2) == 1104:  # AND
        regs[arg3] = regs[arg1] & regs[arg2]

    elif int(opcode, base=2) == 1360:  # ORR
        regs[arg3] = regs[arg1] | regs[arg2]

    elif 160 <= int(opcode, base=2) <= 191:  # B
        # special things must happen here
        return

    elif int(opcode, base=2) in (1160, 1161):  # ADDI
        regs[arg3] = regs[arg1] + arg2

    elif int(opcode, base=2) in (1672, 1673):  # SUBI
        regs[arg3] = regs[arg1] - arg2

    elif 1440 <= int(opcode, base=2) <= 1447:  # CBZ
        if regs[arg3] == 0:
            # more special things
            return

    elif 1448 <= int(opcode, base=2) <= 1455:  # CBNZ
        if regs[arg3] != 0:
            # more special things
            return

    elif 1684 <= int(opcode, base=2) <= 1687:  # MOVZ
        regs[arg3] = 0
        regs[arg3] = arg1 << arg2

    elif 1940 <= int(opcode, base=2) <= 1943:  # MOVK
        regs[arg3] = regs[arg3] + (arg1 << arg2)

    # elif int(opcode, base=2) == 1986:  # LDUR
    # regs[arg3] = data[arg2 - offset]
    # more special things

    elif int(opcode, base=2) == 1984:  # STUR
        while len(data) < arg2:
            data.extend(dataExt)

        base = regs[arg3]
        offset = ((addr[-1] + 4) - base) / 4

        data[arg2 - offset] = regs[arg3]

    elif int(opcode, base=2) == 1872:  # EOR
        regs[arg3] = regs[arg1] ^ regs[arg2]

    elif int(opcode, base=2) == 1690:  # LSR
        regs[arg3] = regs[arg1] >> arg2

    elif int(opcode, base=2) == 1691:  # LSL
        regs[arg3] = regs[arg1] << arg2

    elif int(opcode, base=2) == 1692:  # ASR
        regs[arg3] = regs[arg1] >> arg2


class WriteBackUnit:
    def run(self):
        #print ("INSIDE WRITEBACKUNIT")
        global PostALUBuffer
        simulate_regs(PostALUBuffer)
        PostALUBuffer = None
        #need to write back to registers

class ALUnit:
    def run(self):
        global PostALUBuffer
        PostALUBuffer = (PreALUQueue.get())

class MEMUnit:
    def run(self):
        #print ("INSIDE MEMUnit")
        pass

class IssueUnit:
    def run(self):
        #print ("INSIDE ISSUEUNIT")
        inst1 = PreIssueBuffer.get()
        inst2 = PreIssueBuffer.get()
        if inst1 in ("LDUR", "STUR", "B", "CBZ", "CBNZ"):
            if not PreMEMQueue.full():
                PreMEMQueue.put(inst1)
        else:
            if not PreALUQueue.full():
                PreALUQueue.put(inst1)
        if inst2 in ("LDUR", "STUR", "B", "CBZ", "CBNZ"):
            if not PreMEMQueue.full():
                PreMEMQueue.put(inst2)
        else:
            if not PreALUQueue.full():
                PreALUQueue.put(inst2)


class InstrFetch:
    # eventually needs to fetch from cache
    # getting instruction directly from instruction list for now

    def run(self):
        #print ("INSIDE INSTRFETCH")
        if PreIssueBuffer.full() | instQueue.empty():
            return
        else:
            try:
                PreIssueBuffer.put(instQueue.get())
                #fix this / should determine how much to "put" dynamically
            except:
                return
            try:
                PreIssueBuffer.put(instQueue.get())
            except:
                return

class Processor:
    def __init__(self):
        self.WB = WriteBackUnit()
        self.ALU = ALUnit()
        self.MEM = MEMUnit()
        self.issue = IssueUnit()
        self.fetch = InstrFetch()
        #self.cache = Cache(length=8, delta=5)

    def run(self):
        global cycleNum
        while cycleNum < 5*len(opcode):

            self.fetch.run()
            cycleNum += 1
            self.printState()

            # print ("PREISSUEBUFFER CONTENTS: ")
            # for x in list(PreIssueBuffer.queue):
            #     print x.getInstStr()

            self.issue.run()
            cycleNum += 1
            self.printState()



            # print ("PREISSUEBUFFER CONTENTS: ")
            # for x in list(PreIssueBuffer.queue):
            #     print x.getInstStr()

            self.printState()
            self.fetch.run()
            self.ALU.run()

            # print ("PREISSUEBUFFER CONTENTS: ")
            # for x in list(PreIssueBuffer.queue):
            #     print x.getInstStr()

            self.MEM.run()
            cycleNum += 1

            # print ("PREISSUEBUFFER CONTENTS: ")
            # for x in list(PreIssueBuffer.queue):
            #     print x.getInstStr()

            self.printState()
            self.WB.run()

            cycleNum += 1

            # print ("PREISSUEBUFFER CONTENTS: ")
            # for x in list(PreIssueBuffer.queue):
            #     print x.getInstStr()

    def printState(self):
        print ("--------------------")
        print ("Cycle: " + str(cycleNum))
        print ("Pre-Issue Buffer:")
        for j in range(4):
            print ("\tEntry " + str(j) + ":\t"),
            try:
                print (PreIssueBuffer.queue[j].getInstStr())
            except:
                print "\n"
                continue
        print ("Pre_ALU Queue:")
        for j in range(2):
            print ("\tEntry " + str(j) + ":\t"),
            try:
                print (PreALUQueue.queue[j].getInstStr())
            except:
                print "\n"
                continue
        print ("Post_ALU Queue:")
        print ("\tEntry 0:\t"),
        try:
            print (PostALUBuffer.getInstStr())
        except:
            pass
        print ("Pre_MEM Queue:")
        for j in range(2):
            print ("\tEntry " + str(j) + ":")
        print ("Post_MEM Queue:")
        print ("\tEntry 0:")
        print ("Registers")
        for j in range(32):
            if j % 8 == 0:
                print "R" + str(j).zfill(2) + ":\t",
            print str(regs[j]) + "\t",
            if j % 8 == 7:
                print ("\n"),
        print ("\nCache")
        for j in range(4):
            print ("Set " + str(j) + ":LRU=")
            for k in range(2):  # you'll need to come back and fix this to print queues!!!!!!!!!!!
                print ("\tEntry " + str(k) + ":[(" + "0" + "," + "0" + "," + "0" + ")<" + "," + ">]")
        print ("\nData")


class INST:
    def __init__(self, instNum, opcode_str, arg1Str, arg2Str, arg3Str, opcode, arg1, arg2, arg3):
        self.instNum = instNum
        self.opcode_str = opcode_str
        self.arg1Str = arg1Str
        self.arg2Str = arg2Str
        self.arg3Str = arg3Str
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
    def getInstStr(self):
        return self.opcode_str + " " + self.arg1Str + self.arg2Str + self.arg3Str

class Disassembler:
    # Constructor sets up dummy values, gets I/O files, adds and processes input, and prints disassembled code
    def __init__(self):
        self.input_file_name = 'test9_Rtype_bin.txt'
        self.output_file_name = 'out.txt'
        self.get_io_params()
        self.input_file = open(str(self.input_file_name))
        self.input_to_lists()
        self.print_lists()
        # Simulator(self.input_file_name, self.output_file_name)
        #INST(raw_instruction, opcode, None, None, addr, arg1, arg2, arg3, len(opcode), None, None, None)

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
            instQueue.put(INST(i, opcode_str[i], arg1Str[i], arg2Str[i], arg3Str[i], opcode[i], arg1[i], arg2[i], arg3[i]))

    # returns 2s complement of bin
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
    global processor
    processor = Processor()
    processor.run()
