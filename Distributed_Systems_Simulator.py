#!/usr/bin/python
"""
Vincent Steil
s1008380
Distributed Systems Practical
Distributed_Systems_Simulator.py
Pydoc:
pydoc -w Distributed_Systems_Simulator
"""
import sys
import Process

# input file specs passed through first and second command line args
input_filepath = sys.argv[1]


def read_simulator_input():
    """
    docstring for read_simulator_input
    Read in all the data from the file and store the parsed lines as Operation and Mutex it in the Process dictionary defined in Process.py
    """
    with open(input_filepath, 'r') as f:
        for line in f:
            line = line.split

            if (line[0] == "begin" and line[1] == "process"):
                Process.processes[line[2]] = Process(line[2])
                Process.current_process = line[2]

            #elif line[0] == "end":       
            #    Process.current_process += 1      

            elif (line[0] == "begin" and line[1] == "mutex"):
                Process.processes[Process.current_process].operations.append(Mutex())
                Process.mutex = True

            elif (line[0] == "end" and line[1] == "mutex"):
                Process.mutex = False

            elif line[0] == "send" or line[0] == "recv":
                Process.processes[Process.current_process].logical_time += 1
                if(Process.mutex):              
                    Process.processes[Process.current_process].operations[-1].ops.append(Operation(line[0], Process.processes[Process.current_process], line[2], Process.processes[Process.current_process].logical_time, line[1]))
                else:
                    Process.processes[Process.current_process].operations.append(Operation(line[0], Process.processes[Process.current_process], line[2], Process.processes[Process.current_process].logical_time, line[1]))           

            elif line[0] == "print":
                Process.processes[Process.current_process].logical_time += 1
                if(Process.mutex):
                    Process.processes[Process.current_process].operations[-1].ops.append(Operation(line[0], Process.processes[Process.current_process], line[1], Process.processes[Process.current_process].logical_time,))
                else:
                    Process.processes[Process.current_process].operations.append(Operation(line[0], Process.processes[Process.current_process], line[1], Process.processes[Process.current_process].logical_time,))
         













          