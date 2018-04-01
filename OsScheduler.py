"""
 @file     OsScheduler.py - "main" file
 @author   Jesse Goodspeed
 @date     May 17th, 2017
 @brief    Program that simulates a process scheduler

 To run from "shell prompt", change directory to where current file (and PCB.py) are stored and enter "python3 OsScheduler.py"
"""
##### incorporate paging


from collections import deque
from PCB import *
from decimal import *
import math

# Helper function
def check(value):
    if 0 <= value <= 1:
        return True
    return False

getcontext().prec = 6 # Sets decimal precision to 6 sig. figures

def checkPwr2(value):
    someNumber = math.log(value, 2)
    floorNum = someNumber//1
    if (2**floorNum) == value:
        return True
    return False

def checkPageSize(pgSize, ttlMemSize):
    if checkPwr2(pgSize) and pgSize <= ttlMemSize:
        return True
    return False

# Sys gen phase
print("-- SYS GEN --".center(70))
while True:
    try:
        PrintNum = int(input("    Please specify the NUMBER of system printers: "))
        break
    except ValueError:
        print("Sorry. NOT VALID NUMBER. Please Try again.".rjust(75))
while True:
    try:
        DiskNum = int(input("    Please specify the NUMBER of disk-type devices: "))
        break
    except ValueError:
        print("Sorry. NOT VALID NUMBER. Please try again.".rjust(75))
while True:
    try:
        CdrwNum = int(input("    Please specify the NUMBER of CD/RW-type devices: "))
        break
    except ValueError:
        print("Sorry. NOT VALID NUMBER. Please try again.".rjust(75))
while True:
    try:
        HistParam = float(input("    Please specify the HISTORY PARAMETER [0,1]: "))
        if check(HistParam):
            break
        print("Please enter a VALUE between 0 and 1 inclusive.".rjust(75))
    except ValueError:
        print("Sorry. NOT VALID NUMBER. Please try again.".rjust(75))
while True:
    try:
        InitBurst = int(input("    Please specify initial BURST estimate (milliseconds): "))
        break
    except ValueError:
        print("Sorry. NOT VALID NUMBER. Please try again.".rjust(75))
while True:
    try:
        print("    Please specify the NUMBER of cylinders in each disk: ")
        CylNum = list()
        for i in range(DiskNum):
            number = int(input("Disk " + str(i+1) +": "))
            CylNum.append(number)
        break
    except ValueError:
        print("Sorry. NOT VALID NUMBER. Please try again.".rjust(75))

while True:
    try:
        TotalMemSize = int(input("    Please specify the TOTAL MEMORY SIZE (must be a power of 2): "))
        if checkPwr2(TotalMemSize):
            break
        print("Please enter a VALUE that is equal to a power of 2.".rjust(75))
    except ValueError:
        print("Sorry. NOT VALID NUMBER. Please try again.".rjust(75))

while True:
    try:
        PageSize = int(input("    Please specify the PAGE SIZE (must be a power of 2): "))
        if checkPageSize(PageSize, TotalMemSize):
            break
        print("Please enter a VALUE that is equal to a power of 2 and LESS THAN OR EQUAL \nTO total memory size.".rjust(75))
    except ValueError:
        print("Sorry. NOT VALID NUMBER. Please try again.".rjust(75))

while True:
    try:
        MaxProcessSize = int(input("    Please specify the MAX PROCESS SIZE (number of words): "))
        if MaxProcessSize <= TotalMemSize:
            break
        print("Please enter a VALUE that is LESS THAN OR EQUAL to total memory size.".rjust(75))
    except ValueError:
        print("Sorry. NOT VALID NUMBER. Please try again.".rjust(75))

# Initialize Main Memory
initialFreeFrames = int(TotalMemSize/PageSize)
print("Initial free frames is " + str(initialFreeFrames)) # test
freeFrameList = list(range(initialFreeFrames))
frameTable = list(range(initialFreeFrames))
jobPool = list()
for i in range(initialFreeFrames):
    freeFrameList[i] = i
    frameTable[i] = ["F", None, None]

# Initialize I/O queues according to input specs
printers = list(range(PrintNum))
for i in range(PrintNum):
    printers[i] = deque()

disks = list(range(DiskNum))
for i in range(DiskNum):
    disks[i] = list()
diskHeads = list(range(DiskNum))  # list variable to keep track of head location
for i in range(DiskNum):
    diskHeads[i] = 0  # Initialize each disk head to zero - (PID)

cdrws = list(range(CdrwNum))
for i in range(CdrwNum):
    cdrws[i] = deque()

# Initialize OS Map - data structure that maps location of each PID
osMap = {}

# Running phase
System_Average = (0, 0)
running = True
ready = list()
current_process = PCB(InitBurst)
processId = 1
reminder = "Sorry. INVALID INPUT. Please try again.".rjust(75)
print('\n' +"-- System RUNNING --".center(70))

while(running == True):
    response = False
    forward = False
    retries = 4

    # Input testing
    while (response == False):

        print(" \n Current CPU PROCESS (PID):  "+ str(current_process.pid))
        command = input(" \n What would you like to do?  ====> ")

        response = False

        if command[0] in ('A', 'S') and len(command) == 1:
            response = True
            forward = True
            if current_process.pid != None:
                current_process.addTime()
                ready = sorted(ready, key=lambda x: (x.sjf, x.pid))  # Sorts ready queue SJF
                if len(ready) != 0:
                    if (ready[0].sjf < current_process.sjf):  # Pre-emptive handling
                        current_process.updateTime(HistParam)
                        ready.append(current_process)
                        osMap[current_process.pid] = 'r'  # Update OS map
                        current_process = ready.pop(0)
                        ready = sorted(ready, key=lambda x: (x.sjf, x.pid))
            break
        elif current_process.pid == None and len(freeFrameList)== 0 and command[0] != 'K':
            print("MEMORY IS AT CAPACITY".rjust(75))
            print("Free up memory via terminating a running process.".rjust(75))
            break
        elif command[0] == 'K' and current_process.pid == None and len(command) > 1:
            response = True
            forward = True
            break
        elif current_process.pid == None and len(ready)== 0:
            print("Not so fast. Try ADDING PROCESS to READY queue first.".rjust(75))
            break
        elif command[0] == 't' and len(command) == 1:
            response = True
            forward = True
            current_process.addTime()
            current_process.updateTime(HistParam)
            break
        elif command[0] in ('C', 'D', 'P', 'K', 'c', 'd', 'p') and len(command) > 1:
            try:
                int(command[1:])
            except ValueError:
                print("INVALID INPUT. Please try again.".rjust(75))
                break
            response = True
            forward = True
            current_process.addTime()
            break
        retries = retries - 1
        if retries < 0:
            raise ValueError('invalid user response')
        print(reminder)

    # CPU Execution block
    while forward == True:

        if len(command) == 1:
            # NEW PROCESS INTERRUPT
            if command == 'A':
                newProcess = PCB(InitBurst, processId)
                # ready.append(PCB(InitBurst, processId))
                processId += 1
                # Prompt for size of new process
                while True:
                    try:
                        ProcessSize = int(input("    What is the SIZE of this new process? (number of words): "))
                        if ProcessSize <= MaxProcessSize:
                            if ProcessSize/PageSize <= len(freeFrameList):  # Check for free frames
                                number = math.ceil(ProcessSize/PageSize)
                                for i in range(number):
                                    fTableIndex = freeFrameList[0]
                                    frameTable[fTableIndex][0] = "A"
                                    frameTable[fTableIndex][1] = newProcess.pid
                                    frameTable[fTableIndex][2] = len(newProcess.page_table)
                                    newProcess.page_table.append(freeFrameList.pop(0))
                                ready.append(newProcess)
                                osMap[newProcess.pid] = 'r'  # Update OS map
                                print("New process added to READY".rjust(75))
                            else:
                                jobPool.append((newProcess, ProcessSize))
                                # sort by processSize, descending order
                                jobPool = sorted(jobPool, key=lambda process: process[1], reverse=True)
                                print("New process added to JOB POOL".rjust(75))
                            break
                        print("Please enter a VALUE that is LESS THAN OR EQUAL to MAX process size.".rjust(75),\
                              "("+str(MaxProcessSize)+")")
                    except ValueError:
                        print("Sorry. NOT VALID NUMBER. Please try again.".rjust(75))

                if current_process.pid == None:
                        try:
                            current_process = ready.pop(0)
                            break
                        except IndexError:
                            print("MEMORY IS FULL".rjust(75))
                            print("All new processes will be added to Job Pool until memory frees up.".rjust(75))

                break
            # TERMINATE PROCESS sys call
            elif command == 't':
                try:
                    # Termination Reportage
                    print("TERMINATED process: ".rjust(65), \
                          '\n' + "PID: ".rjust(60), str(current_process.pid), \
                          '\n' + "Ttl CPU Time = ".rjust(60), str(current_process.ttl_cpu_time),\
                          '\n' + "Avg BURST Time = ".rjust(60), str(current_process.avg_burst))
                    System_Average = current_process.sysAvg(System_Average[0], System_Average[1])
                    osMap[current_process.pid] = 't'  # Update OS map
                    # Code block to free up memory for terminated process
                    for i in range(len(current_process.page_table)):
                        index = current_process.page_table[i]
                        frameTable[index][0] = 'F'
                        freeFrameList.append(index)
                    deleteList = list()
                    # Job pool dispatches biggest process that will fit free frames
                    for i in range(len(jobPool)):
                        ProcessSize = jobPool[i][1]
                        process = jobPool[i][0]
                        if ProcessSize/PageSize <= len(freeFrameList):  # Check for free frames
                            number = math.ceil(ProcessSize/PageSize)
                            # Update to frame table
                            for elem in range(number):
                                fTableIndex = freeFrameList[0]
                                frameTable[fTableIndex][0] = "A"
                                frameTable[fTableIndex][1] = process.pid
                                frameTable[fTableIndex][2] = len(process.page_table)
                                process.page_table.append(freeFrameList.pop(0))
                            ready.append(process)
                            osMap[process.pid] = 'r'  # Update OS map
                            #del jobPool[i]
                            deleteList.append((process, ProcessSize))
                            print("JOB POOL dispatched a new process to READY".rjust(75))
                    for i in range(len(deleteList)):
                        jobPool.remove(deleteList[i])
                    current_process = ready.pop(0)
                except IndexError:
                    current_process = PCB(InitBurst)
                    print("READY QUEUE EMPTY".rjust(75))
                print("Current process TERMINATED and SystemAvg UPDATED".rjust(75))
                break
            # SNAPSHOT INTERRUPT
            elif command == 'S':
                choice = None
                while True:     # Error Handling
                    choice = input("Select c, d, j, m, p, OR r: ")
                    if choice in ('c', 'C', 'd', 'D', 'j', 'J', 'm', 'M', 'p', 'P', 'r', 'R') and (len(choice) == 1):
                        break
                    else:
                        print("INVALID INPUT. Please try again.".rjust(75))

                if choice in ('c', 'C'):
                    print("/CDRWS/","SYS AVG Ttl CPU time: ".rjust(54), str(System_Average[1]),\
                          "\nPID".ljust(5), "Name".ljust(5), "MemStart".ljust(10), "R/W".ljust(5), \
                          "Length".ljust(5), "CPUtime".ljust(5), "AvgBurst".ljust(5), "PgTbl".ljust(8))
                    for x in range(len(cdrws)):
                        print("---c"+str(x+1))
                        for elem in cdrws[x]:
                            print(str(elem.pid).ljust(5), elem.file_name.ljust(5), str(elem.mem_start).ljust(10), \
                                  elem.rw.ljust(5), str(elem.file_length).ljust(5), str(elem.ttl_cpu_time).ljust(7), \
                                  str(elem.avg_burst).ljust(8), str(elem.page_table).ljust(8))

                elif choice in ('d', 'D'):
                    print("/DISKS/", "SYS AVG Ttl CPU time: ".rjust(54), str(System_Average[1]),\
                          "\nPID".ljust(5), "Name".ljust(5), "CylNum".ljust(10), "MemStart".ljust(10), \
                          "R/W".ljust(5), "Length".ljust(5), "CPUtime".ljust(5), "AvgBurst".ljust(5), "PgTbl".ljust(8))
                    for x in range(len(disks)):
                        print("---d"+str(x+1))
                        for elem in disks[x]:
                            print(str(elem.pid).ljust(5), elem.file_name.ljust(5), str(elem.cyl).ljust(10), \
                                  str(elem.mem_start).ljust(10), elem.rw.ljust(5), str(elem.file_length).ljust(5), \
                                  str(elem.ttl_cpu_time).ljust(7), str(elem.avg_burst).ljust(8), str(elem.page_table).ljust(8))

                elif choice in ('j', 'J'):
                    print("/JOB POOL/"+'\n',
                          "PID".ljust(5), "Size".ljust(5))
                    if len(jobPool) < 1:
                        print("-- POOL IS EMPTY --".center(35))
                    else:
                        for i in range(len(jobPool)):
                            print(" "+str(jobPool[i][0].pid).ljust(5),str(jobPool[i][1]).ljust(5))

                elif choice in ('m', 'M'):
                    print("/SYS MEM/"+"\nFrame".ljust(5), "Status(F/A)".ljust(5), "PID".ljust(5), "Page#".ljust(5))
                    for i in range(len(frameTable)):
                        print(str(i).ljust(9), str(frameTable[i][0]).ljust(7), str(frameTable[i][1]).ljust(5), \
                              str(frameTable[i][2]).ljust(5))
                    print("Free-Frame List: " + str(freeFrameList))

                elif choice in ('p', 'P'):
                    print("/PRINTERS/","SYS AVG Ttl CPU time: ".rjust(54), str(System_Average[1]),\
                          "\nPID".ljust(5), "Name".ljust(5), "MemStart".ljust(10), "R/W".ljust(5), \
                          "Length".ljust(5), "CPUtime".ljust(5), "AvgBurst".ljust(5), "PgTbl".ljust(8))
                    for x in range(len(printers)):
                        print("---p"+str(x+1))
                        for elem in printers[x]:
                            print(str(elem.pid).ljust(5), elem.file_name.ljust(5), str(elem.mem_start).ljust(10), \
                                  elem.rw.ljust(5), str(elem.file_length).ljust(5), str(elem.ttl_cpu_time).ljust(7), \
                                  str(elem.avg_burst).ljust(8), str(elem.page_table).ljust(8))

                else:
                    print("/READY/","SYS AVG Ttl CPU time: ".rjust(54), str(System_Average[1]),\
                          "\nPID".ljust(5), "Name".ljust(5), "MemStart".ljust(10), "R/W".ljust(5), \
                          "Length".ljust(5), "CPUtime".ljust(5), "AvgBurst".ljust(5),"TAU".ljust(5), "PgTbl".ljust(8))
                    if len(ready) < 1:
                        print("-- QUEUE IS EMPTY --".center(35))
                    else:
                        for elem in ready:
                            print(str(elem.pid).ljust(5), str(elem.file_name).ljust(5), str(elem.mem_start).ljust(10), \
                                  str(elem.rw).ljust(5), str(elem.file_length).ljust(5), str(elem.ttl_cpu_time).ljust(7), \
                                  str(elem.avg_burst).ljust(8), str(elem.sjf).ljust(5), str(elem.page_table).ljust(8))
                break

        index = (int(command[1:]) - 1) # Initialize index and -1 to include 0
        if index < 0: # Error handling
            print(str(command + " is out of bounds. Please try again.").rjust(75))
            break

        # SYSTEM CALLS
        elif command[0] in ('c', 'd', 'p') and (current_process != None):
            # Prompts user for PCB data
            if command[0] == 'c' and (index < len(cdrws)):
                current_process.updateTime(HistParam)
                current_process.SetName()
                current_process.SetLocation(TotalMemSize, PageSize)
                current_process.SetInstruct()
                cdrws[index].append(current_process)
                osMap[current_process.pid] = 'c'+str(index)  # Update OS map
                print(str("Current PROCESS MOVED to c" + str(index+1) + " queue").rjust(75))
                if len(ready) > 0:
                    current_process = ready.pop(0)
                else:
                    current_process = PCB(InitBurst)
                    print("READY QUEUE EMPTY - Please add process".rjust(75))
            elif command[0] == 'd' and (index < len(disks)):
                current_process.updateTime(HistParam)
                current_process.SetName()
                current_process.SetLocation(TotalMemSize, PageSize)
                current_process.SetInstruct()
                current_process.CylAccess(CylNum[index])  # Cylinder access prompt

                disks[index].append(current_process)
                osMap[current_process.pid] = 'd'+str(index)  # Update OS map
                if diskHeads[index] == 0: #  "If diskHead is serving PID 0"
                    disks[index] = sorted(disks[index], key=lambda x: (x.cyl, x.mem_start)) #  Sorts disk queue by cylinder
                    diskHeads[index] = disks[index][0].pid  # Adjust disk head
                else:
                    queueList = sorted(disks[index], key=lambda x: (x.cyl, x.mem_start))
                    location = 0
                    for i in range(len(queueList)):
                        if queueList[i].pid == diskHeads[index]:
                            location = i
                            break
                    for i in range(len(queueList)):
                        disks[index][i] = queueList[(location+i)%len(queueList)]  # Reorders queue based on disk head position

                print(str("Current PROCESS MOVED to d" + str(index+1) + " queue").rjust(75))
                if len(ready) > 0:
                    current_process = ready.pop(0)
                else:
                    current_process = PCB(InitBurst)
                    print("READY QUEUE EMPTY - Please add process".rjust(75))

            elif command[0] == 'p' and (index < len(printers)):
                current_process.updateTime(HistParam)
                current_process.SetName()
                current_process.SetLocation(TotalMemSize, PageSize)
                current_process.RWaction('w')
                printers[index].append(current_process)
                osMap[current_process.pid] = 'p'+str(index)  # Update OS map
                print(str("Current PROCESS MOVED to p" + str(index+1) + " queue").rjust(75))
                if len(ready) > 0:
                    current_process = ready.pop(0)
                else:
                    current_process = PCB(InitBurst)
                    print("READY QUEUE EMPTY - Please add process".rjust(75))

            else:
                print(str(command[0]+ str(index + 1) + " does not exist. Please try again.").rjust(75))
            break

        # DEVICE INTERRUPTS
        elif command[0] in ('C', 'D', 'P', 'K'):
            if command[0] == 'C' and (index < len(cdrws)):
                try:  # Error handling

                    ready.append(cdrws[index].popleft())
                    osMap[ready[len(ready)-1].pid] = 'r'  # Update OS map
                    ready = sorted(ready, key=lambda x: (x.sjf, x.pid))
                    if (ready[0].sjf < current_process.sjf):
                        ready.append(current_process)
                        current_process = ready.pop(0)
                        ready = sorted(ready, key=lambda x: (x.sjf, x.pid))
                    print("Task completed".rjust(75))
                except IndexError:
                    print("QUEUE EMPTY - please try something else".rjust(75))
            elif command[0] == 'D' and (index < len(disks)):
                try:
                    ready.append(disks[index].pop(0))
                    osMap[ready[len(ready)-1].pid] = 'r'  # Update OS map
                    ready = sorted(ready, key=lambda x: (x.sjf, x.pid))
                    if (ready[0].sjf < current_process.sjf):
                        ready.append(current_process)
                        current_process = ready.pop(0)
                        ready = sorted(ready, key=lambda x: (x.sjf, x.pid))
                    diskHeads[index] = disks[index][0].pid  #  Adjust disk head
                    print("Task completed".rjust(75))
                except IndexError:
                    print("QUEUE EMPTY - please try something else".rjust(75))
            elif command[0] == 'P' and (index < len(printers)):
                try:
                    ready.append(printers[index].popleft())
                    osMap[ready[len(ready)-1].pid] = 'r'  # Update OS map
                    ready = sorted(ready, key=lambda x: (x.sjf, x.pid))
                    if (ready[0].sjf < current_process.sjf):
                        ready.append(current_process)
                        current_process = ready.pop(0)
                        ready = sorted(ready, key=lambda x: (x.sjf, x.pid))
                    print("Task completed".rjust(75))
                except IndexError:
                    print("QUEUE EMPTY - please try something else".rjust(75))
            elif command[0] == 'K':
                if int(command[1:]) in osMap:
                    key = int(command[1:])
                    location = osMap[key]  # t, r, dx, cx, or px - indicates location of PID
                    if location == 't':
                        print("Process is already TERMINATED".rjust(75))
                    if location == 'r':
                        for i in range(len(ready)):
                            if ready[i].pid == key:
                                targetP = ready[i]
                                del ready[i]
                                # Termination Reportage
                                print("TERMINATED process: ".rjust(65), \
                                      '\n' + "PID: ".rjust(60), str(targetP.pid), \
                                      '\n' + "Ttl CPU Time = ".rjust(60), str(targetP.ttl_cpu_time),\
                                      '\n' + "Avg BURST Time = ".rjust(60), str(targetP.avg_burst))
                                System_Average = targetP.sysAvg(System_Average[0], System_Average[1])
                                osMap[targetP.pid] = 't'  # Update OS map
                                # Code block to free up memory for terminated process
                                for elem in range(len(targetP.page_table)):
                                    index = targetP.page_table[elem]
                                    frameTable[index][0] = 'F'
                                    freeFrameList.append(index)
                                deleteList = list()
                                # Job pool dispatches biggest process that will fit free frames
                                for item in range(len(jobPool)):
                                    ProcessSize = jobPool[item][1]
                                    process = jobPool[item][0]
                                    if ProcessSize/PageSize <= len(freeFrameList):  # Check for free frames
                                        number = math.ceil(ProcessSize/PageSize)
                                        # Update to frame table
                                        for elem in range(number):
                                            fTableIndex = freeFrameList[0]
                                            frameTable[fTableIndex][0] = "A"
                                            frameTable[fTableIndex][1] = process.pid
                                            frameTable[fTableIndex][2] = len(process.page_table)
                                            process.page_table.append(freeFrameList.pop(0))
                                        ready.append(process)
                                        osMap[process.pid] = 'r'  # Update OS map
                                        #del jobPool[item]
                                        deleteList.append((process, ProcessSize))
                                        print("JOB POOL dispatched a new process to READY".rjust(75))
                                for i in range(len(deleteList)):
                                    jobPool.remove(deleteList[i])
                    if location[0] == 'd':
                        pos = int(location[1:])
                        for item in range(len(disks[pos])):
                            if disks[pos][item].pid == key:
                                targetP = disks[pos][item]
                                del disks[pos][item]
                                # Termination Reportage
                                print("TERMINATED process: ".rjust(65), \
                                      '\n' + "PID: ".rjust(60), str(targetP.pid), \
                                      '\n' + "Ttl CPU Time = ".rjust(60), str(targetP.ttl_cpu_time),\
                                      '\n' + "Avg BURST Time = ".rjust(60), str(targetP.avg_burst))
                                System_Average = targetP.sysAvg(System_Average[0], System_Average[1])
                                osMap[targetP.pid] = 't'  # Update OS map
                                # Code block to free up memory for terminated process
                                for elem in range(len(targetP.page_table)):
                                    index = targetP.page_table[elem]
                                    frameTable[index][0] = 'F'
                                    freeFrameList.append(index)
                                deleteList = list()
                                # Job pool dispatches biggest process that will fit free frames
                                for item in range(len(jobPool)):
                                    ProcessSize = jobPool[item][1]
                                    process = jobPool[item][0]
                                    if ProcessSize/PageSize <= len(freeFrameList):  # Check for free frames
                                        number = math.ceil(ProcessSize/PageSize)
                                        # Update to frame table
                                        for elem in range(number):
                                            fTableIndex = freeFrameList[0]
                                            frameTable[fTableIndex][0] = "A"
                                            frameTable[fTableIndex][1] = process.pid
                                            frameTable[fTableIndex][2] = len(process.page_table)
                                            process.page_table.append(freeFrameList.pop(0))
                                        ready.append(process)
                                        osMap[process.pid] = 'r'  # Update OS map
                                        #del jobPool[item]
                                        deleteList.append((process, ProcessSize))
                                        print("JOB POOL dispatched a new process to READY".rjust(75))
                                for i in range(len(deleteList)):
                                    jobPool.remove(deleteList[i])
                    if location[0] == 'c':
                        pos = int(location[1:])
                        for item in range(len(cdrws[pos])):
                            if cdrws[pos][item].pid == key:
                                targetP = cdrws[pos][item]
                                del cdrws[pos][item]
                                # Termination Reportage
                                print("TERMINATED process: ".rjust(65), \
                                      '\n' + "PID: ".rjust(60), str(targetP.pid), \
                                      '\n' + "Ttl CPU Time = ".rjust(60), str(targetP.ttl_cpu_time),\
                                      '\n' + "Avg BURST Time = ".rjust(60), str(targetP.avg_burst))
                                System_Average = targetP.sysAvg(System_Average[0], System_Average[1])
                                osMap[targetP.pid] = 't'  # Update OS map
                                # Code block to free up memory for terminated process
                                for elem in range(len(targetP.page_table)):
                                    index = targetP.page_table[elem]
                                    frameTable[index][0] = 'F'
                                    freeFrameList.append(index)
                                deleteList = list()
                                # Job pool dispatches biggest process that will fit free frames
                                for item in range(len(jobPool)):
                                    ProcessSize = jobPool[item][1]
                                    process = jobPool[item][0]
                                    if ProcessSize/PageSize <= len(freeFrameList):  # Check for free frames
                                        number = math.ceil(ProcessSize/PageSize)
                                        # Update to frame table
                                        for elem in range(number):
                                            fTableIndex = freeFrameList[0]
                                            frameTable[fTableIndex][0] = "A"
                                            frameTable[fTableIndex][1] = process.pid
                                            frameTable[fTableIndex][2] = len(process.page_table)
                                            process.page_table.append(freeFrameList.pop(0))
                                        ready.append(process)
                                        osMap[process.pid] = 'r'  # Update OS map
                                        #del jobPool[item]
                                        deleteList.append((process, ProcessSize))
                                        print("JOB POOL dispatched a new process to READY".rjust(75))
                                for i in range(len(deleteList)):
                                    jobPool.remove(deleteList[i])
                    if location[0] == 'p':
                        pos = int(location[1:])
                        for item in range(len(printers[pos])):
                            if printers[pos][item].pid == key:
                                targetP = printers[pos][item]
                                del printers[pos][item]
                                # Termination Reportage
                                print("TERMINATED process: ".rjust(65), \
                                      '\n' + "PID: ".rjust(60), str(targetP.pid), \
                                      '\n' + "Ttl CPU Time = ".rjust(60), str(targetP.ttl_cpu_time),\
                                      '\n' + "Avg BURST Time = ".rjust(60), str(targetP.avg_burst))
                                System_Average = targetP.sysAvg(System_Average[0], System_Average[1])
                                osMap[targetP.pid] = 't'  # Update OS map
                                # Code block to free up memory for terminated process
                                for elem in range(len(targetP.page_table)):
                                    index = targetP.page_table[elem]
                                    frameTable[index][0] = 'F'
                                    freeFrameList.append(index)
                                deleteList = list()
                                # Job pool dispatches biggest process that will fit free frames
                                for item in range(len(jobPool)):
                                    ProcessSize = jobPool[item][1]
                                    process = jobPool[item][0]
                                    if ProcessSize/PageSize <= len(freeFrameList):  # Check for free frames
                                        number = math.ceil(ProcessSize/PageSize)
                                        # Update to frame table
                                        for elem in range(number):
                                            fTableIndex = freeFrameList[0]
                                            frameTable[fTableIndex][0] = "A"
                                            frameTable[fTableIndex][1] = process.pid
                                            frameTable[fTableIndex][2] = len(process.page_table)
                                            process.page_table.append(freeFrameList.pop(0))
                                        ready.append(process)
                                        osMap[process.pid] = 'r'  # Update OS map
                                        deleteList.append((process, ProcessSize))
                                        print("JOB POOL dispatched a new process to READY".rjust(75))
                                        if current_process.pid == None and len(ready) > 0 :
                                            current_process = ready.pop(0)
                                for i in range(len(deleteList)):
                                    jobPool.remove(deleteList[i])
                else:
                    print("This process does not exist in main memory.".rjust(75))

            else:
                print(str(command[0].lower() + str(index + 1) + " does not exist. Please try again.").rjust(75))
            break
        break




if __name__ == "__main__":
    import sys
