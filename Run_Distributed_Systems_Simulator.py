#!/usr/bin/python
"""
Vincent Steil
s1008380
Distributed Systems Practical
Run_Distributed_Systems_Simulator.py
Pydoc:
pydoc -w Run_Distributed_Systems_Simulator


to run:
    Run_Distributed_Systems_Simulator.py -i <inputfile> -o <outputfile>
    pypy Run_Distributed_Systems_Simulator.py -i in1.txt -o out1.txt
"""


from Distributed_Systems_Simulator import read_simulator_input, run_simulator, set_IO
from Process_DS import print_ordered_all_operations
import sys, getopt


IO =  set_IO(sys.argv[1:])
input_file = IO[0]
output_file =IO[1]

print input_file
print output_file

print("Calling read_simulator_input")
read_simulator_input(input_file)
print("Calling run_simulator")
run_simulator()
print("Calling print_ordered_all_operations")
print_ordered_all_operations(output_file)