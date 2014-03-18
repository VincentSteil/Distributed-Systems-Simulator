#!/usr/bin/python
"""
Vincent Steil
s1008380
Distributed Systems Practical
Process.py
Pydoc:
pydoc -w Process_DS
"""

from __future__ import print_function
import sys
import collections



"""
dictionary of Processes
Processes do not need to be stored in an ordered fashion. This lets us store the key to each process in each operation for both host_process and target_process
"""

class Process:
    """
    docstring for Process
    Contains a list of Operation and Mutex blocks and keeps track of local Lampard Clock Time
    Assume that all Processes know of all other Processes
    """
    processes = collections.OrderedDict()     
    current_process = None
    mutex_block = False                           # only used while initially reading in data from file not during mutex arbitration

    # process state definitions
    released = 0    # Not in or requiring entry to the critical section (Mutex block)
    wanted = 1      # Requiring entry to the critical section
    held = 2        # Currently has access to critical section

    # operations can be Operation or Mutex
    def __init__(self, name):
        self.operations = []
        self.logical_time = 0
        self.name = name
        self.status = Process.released                    # keeps track of mutual exclusion enforcement state for Ricarta & Agrawala algorithm   
        self.received_messages = collections.OrderedDict() # key = (sender_name,content) leads to list of timestamps for that msg (to enable duplicates)     
        self.operation_counter = 0
        self.mtx_req_send_time = None             # ID is implicitely stored, time_stamp is explicitely stored
        self.mtx_req_grant_recv_set = set()

    @classmethod
    def dump_data_console(Pro):
        """
        debug data dump to the console
        """
        for pro in Pro.processes.values():
            print(pro.name, pro.operation_counter)      
            for ops in pro.operations:
                ops.print_op_console()

class Mutex:
        """
        docstring for Mutex
        Mutex datastructure
        contains multiple Operation
        must be run in a single block
        """
        def __init__(self):
              self.operations = []
              self.mutex_operation_offset = 0

        def print_operation(self, output):
            """
            print the entire block to file output
            """
            for op in self.operations:
                if op.operation_type == "print":
                    print("printed", op.host_process, op.content, op.logical_time, file = output)
                elif op.operation_type == "send":
                    print("sent", op.host_process, op.content, op.target_process, op.logical_time, file = output)
                elif op.operation_type == "recv":
                    print("received", op.host_process, op.content, op.target_process, op.logical_time, file = output)
                else:
                    # shit went wrong badly for this to happen, mtx msgs should NEVER turn up in a mutex block
                    print("Tried to write a mtx_msg to file")

        def print_op_console(self):
            """
            print the entire block to the console
            """
            for op in self.operations:
                if op.operation_type == "print":
                    print("printed", op.host_process, op.content, op.logical_time)
                elif op.operation_type == "send":
                    print("sent", op.host_process, op.content, op.target_process, op.logical_time)
                elif op.operation_type == "recv":
                    print("received", op.host_process, op.content, op.target_process, op.logical_time)
                else:
                    # shit went wrong badly for this to happen, mtx msgs should NEVER turn up in a mutex block
                    print("Tried to write a mtx_msg to file", op.operation_type)

        def __len__(self):
            return 1
                    

class Operation:
    """
    docstring for Operation
    Operation datastructure
    Basic datastructure for the simulator
    operation_type can be:
        recv
        send
        print
        mtx_req_send
        mtx_req_recv
        mtx_req_grant_send
        mtx_req_grant_recv
    """
    def __init__(self, operation_type, host_process, content, logical_time, mutex, target_process = None, multicast_logical_time = None):
        self.operation_type = operation_type
        self.host_process = host_process
        self.content = content
        self.logical_time = logical_time
        self.target_process = target_process
        self.mutex = mutex
        self.multicast_logical_time = multicast_logical_time

    def __len__(self):
        return 1

    def print_operation(self, output):
        """
        Prints operation to the file defined in outputfile
        Prints error msg to console if trying to print mtx_msg
        """
        if self.operation_type == "print":
            print("printed", self.host_process, self.content, self.logical_time, file = output)
        elif self.operation_type == "send":
            print("sent", self.host_process, self.content, self.target_process, self.logical_time, file = output)
        elif self.operation_type == "recv":
            print("received", self.host_process, self.content, self.target_process, self.logical_time, file = output)
        else:
            print("Tried to write a mtx_msg to file")

    def print_op_console(self):
        """
        Prints operation to console
        Can print all operation_type
        """
        if self.operation_type == "print":
            print ("printed", self.host_process, self.content, self.logical_time) 
        elif self.operation_type == "send":
            print ("sent", self.host_process, self.content, self.target_process, self.logical_time) 
        elif self.operation_type == "recv":
            print ("received", self.host_process, self.content, self.target_process, self.logical_time)
        else:
            print (self.operation_type, self.host_process, self.target_process, self.logical_time)
            
                 
def print_ordered_all_operations(outputfile):
    """
    print all standard print,send,recv operations to a file and those + mtx to console
    """
    print("Start printing real ops to file")
    output = open(outputfile, 'w')
    i = 0
    # current_Lampard_value starts at two such that all ops with logical_time == 1 can be printed
    current_Lampard_value = 1
    max_ops = 1
    #reset op counters

    print("")

    print("Operations content of all processes")

    for pro in Process.processes.values():
        pro.operation_counter = 0 

        print("")  
        print(pro.name)   

        for ops in pro.operations:
            ops.print_op_console()
        
    print("")
    print("")
    print("")


    no_more_ops = False
    print("Ordered operations")
    print("")
    while not no_more_ops:
        # flag is deactivated again if there is a process with ops in it
        no_more_ops = True
        # pro is the current process being executed
        for pro in Process.processes.values():

            if pro.operation_counter < len(pro.operations):               
                no_more_ops = False

                op = pro.operations[pro.operation_counter]
                if isinstance(op, Mutex):
                    if op.operations[0].logical_time <= current_Lampard_value:
                        op.print_operation(output)
                        op.print_op_console()
                        # update current_Lampard_value to logical_time of last operation in the mutex block
                        current_Lampard_value = max(current_Lampard_value, op.operations[-1].logical_time + 1)
                        pro.operation_counter += 1

                elif op.logical_time <= current_Lampard_value:      
                    # print a single send, recv, print instruction print isn't strictly necessary in the below instruction, as print is always a mutex op
                    if op.operation_type in ["send","recv"]:
                        op.print_operation(output)
                        op.print_op_console()
                        pro.operation_counter += 1
                        current_Lampard_value = max(current_Lampard_value, op.logical_time + 1)

                    # if dealing with mutex arbitration messages, increment op counter, print to console, and continue
                    elif op.operation_type in ["mtx_req_send" ,"mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]:
                        op.print_op_console()
                        pro.operation_counter += 1
                        current_Lampard_value = max(current_Lampard_value, op.logical_time + 1)

    print("Finished printing to file")
    output.close()
           















