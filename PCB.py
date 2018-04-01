"""
 @file     PCB.py
 @author   Jesse Goodspeed
 @date     May 17th, 2017
 @brief    script that defines PCB class
"""
from decimal import *
import math
#from .comparable import *

# PCB class definition
class PCB:

    # Initializes new PCB object with PID passed as parameter
    def __init__(self, initialVal, number=None):
        self.pid = number
        self.file_name = None
        self.mem_start = None
        self.rw = None
        self.file_length = None
        self.cpu_time = 0  # Counts time for current CPU burst
        self.ttl_cpu_time = 0
        self.cpu_num = 0
        self.avg_burst = None
        self.sjf = initialVal  # initial burst estimate
        self.cyl = None
        self.page_table = list()

    def NameFile(self, name):
        self.file_name = name

    def SetName(self, prompt = "What is the FILE NAME?: "):
        self.NameFile(input(prompt))

    def MemLocation(self, location):
        self.mem_start = location

    def SetLocation(self, memSize, pgSize, prompt = "What is the MEMORY LOCATION?: "):
        while True:
            try:
                logAddr = int(input(prompt), base=16)  # Input is read as hex-integer
               # decAddr = hex(logAddr)  # Decimal form
                binAddr = bin(logAddr)  # Binary form
                if logAddr < memSize:
                    phyAddrLen = math.floor(math.log(memSize, 2))  # Bit length of physical address
                    offset = math.floor(math.log(pgSize, 2))  # Bit length of offset
                    cutoff = (phyAddrLen - offset) +2  # Where to cut logical address for page #
                    pageNum = int(binAddr[:cutoff], base=2)
                    if pageNum < len(self.page_table):
                        frameNum = self.page_table[pageNum]
                        binPhyAddr = bin(frameNum)+binAddr[cutoff:]
                        decPhyAddr = int(binPhyAddr, base=16)
                        physAddr = hex(decPhyAddr)
                        break
                    else:
                        print("Sorry! That MEMORY LOCATION does not exist in the page table. Try again.".rjust(75))
                else:
                    print("Sorry! That MEMORY LOCATION does not exist in the memory space. Try again.".rjust(75))
            except ValueError:
                print("Sorry! That was not a valid MEMORY LOCATION (hexidecimal). Try again.".rjust(75))
        print("Physical Address: "+physAddr)
        self.MemLocation(physAddr)
        return None

    def SetInstruct(self, prompt = "Is this a call for a READ or WRITE instruction? (R/W): "):
        while True:
            action = input(prompt)
            if action not in ('w', 'r', 'W', 'R'):
                print("Invalid input. Please try again.".rjust(75))
            else:
                self.RWaction(action)
                return None

    def FileLength(self, length):
        self.file_length = length

    def SetFileLength(self, prompt = "What is the FILE LENGTH?(quantity): "):
        while True:
            try:
                length = int(input(prompt))
                break
            except ValueError:
                print("Sorry! That was not a valid number. Please try again.".rjust(75))
        self.FileLength(length)
        return None

    def RWaction(self, action):
        if action in ('W', 'w'):
            action = 'w'
            self.SetFileLength()
        elif action in ('R', 'r'):
            action = 'r'
        self.rw = action

    def SetCyl(self, number):
        self.cyl = number

    def CylAccess(self, limit, prompt = "Which CYLINDER to access for this instruction? "):
        response = False
        while response == False:
            try:
                cylAddy = int(input(prompt))
                if (cylAddy-1) < limit and cylAddy > 0:
                    response = True
                else:
                    print("Sorry! That CYLINDER does not exist. Please try again.".rjust(75))
            except ValueError:
                print("Sorry! That was not a valid number. Please try again.".rjust(75))
        self.SetCyl(cylAddy)
        return None

    def updateTime(self, hxParam):
        self.ttl_cpu_time += self.cpu_time
        self.cpu_num += 1
        self.avg_burst = Decimal(self.ttl_cpu_time)/Decimal(self.cpu_num)
        self.sjf = (hxParam * self.sjf) + ((1-hxParam)*self.cpu_time)
        self.cpu_time = 0

    def increaseTime(self, timeIncrease):
        self.cpu_time += timeIncrease

    def addTime(self, prompt = "How long did this process use the CPU? (milliseconds): "):
        while True:
            try:
                time = int(input(prompt))
                break
            except ValueError:
                print("Sorry! That was not a valid number. Please try again.".rjust(75))
        self.increaseTime(time)
        return None

    def sysAvg(self, processCount, average):
        prevTtl = average * processCount  # average * total completed processes
        processCount += 1
        average = Decimal(prevTtl + self.ttl_cpu_time)/Decimal(processCount)
        return (processCount, average)
