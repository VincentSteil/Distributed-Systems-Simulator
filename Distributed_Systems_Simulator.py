#!/usr/bin/python
"""
Vincent Steil
s1008380
Distributed Systems Practical
Distributed_Systems_Simulator.py
"""
import sys
import Process.py

# input and output file specs passed through first and second command line args
input_filepath = sys.argv[1]
output_file = open(sys.argv[2], 'w')

# list of Process'
processes = []
mutex = False

"""
Read in all the data from the file and store it in the datastructures defined in Process.py
"""
with open(filepath, 'r') as f:
    for line in f:
        line = line.split

        if (line[0] == "begin" && line[1] == "process"):
            processes.append(Process(line[2]))

        elif line[0] == "end":       
            Process.current_process += 1

        elif (line[0] == "begin" && line[1] == "mutex"):
            processes[Process.current_process].operations.append(Mutex())
            mutex = True

        elif (line[0] == "end" && line[1] == "mutex"):
            mutex = False

        elif line[0] == "send" || line[0] == "recv"
            processes[Process.current_process].logical_time += 1
            if(mutex):              
                processes[Process.current_process].operations[-1].ops.append(Operation(line[0], processes[Process.current_process], line[2], processes[Process.current_process].logical_time, line[1]))
            else:
                processes[Process.current_process].operations.append(Operation(line[0], processes[Process.current_process], line[2], processes[Process.current_process].logical_time, line[1]))           

        elif line[0] == "print"
            processes[Process.current_process].logical_time += 1
            if(mutex):
                processes[Process.current_process].operations[-1].ops.append(Operation(line[0], processes[Process.current_process], line[1], processes[Process.current_process].logical_time,))
            else:
                processes[Process.current_process].operations.append(Operation(line[0], processes[Process.current_process], line[1], processes[Process.current_process].logical_time,))
 













          