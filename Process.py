#!/usr/bin/python
"""
Vincent Steil
s1008380
Distributed Systems Practical
Process.py
Pydoc:
pydoc -w Process
"""

from __future__ import print_function
import sys
import collections


# process state definitions
released = 0    # Not in or requiring entry to the critical section (Mutex block)
wanted = 1      # Requiring entry to the critical section
held = 2        # Currently has access to critical section

"""
dictionary of Processes
Processes do not need to be stored in an ordered fashion. This lets us store the key to each process in each operation for both host_process and target_process
"""
processes = collections.OrderedDict() 

class Process:
    """
    docstring for Process
    Contains a list of Operation and Mutex blocks and keeps track of local Lampard Clock Time
    Assume that all Processes know of all other Processes
    """
        
    current_process = None
    mutex_block = False                           # only used while initially reading in data from file not during mutex arbitration

    # operations can be Operation or Mutex
    def __init__(self, name):
        self.operations = []
        self.logical_time = 0
        self.name = name
        self.status = released                    # keeps track of mutual exclusion enforcement state for Ricarta & Agrawala algorithm   
        self.received_messages = collections.OrderedDict() # key = (sender_name,content) leads to list of timestamps for that msg (to enable duplicates)     
        self.operation_counter = 0
        self.mtx_req_send_time = None             # ID is implicitely stored, time_stamp is explicitely stored
        self.mtx_req_grant_recv_set = set()

class Mutex:
        """
        docstring for Mutex
        """
        def __init__(self):
              self.operations = []
              self.mutex_operation_offset = 0

        def print_operation(self):
            for op in self.operations:
                if op.operation_type == "print":
                    print("printed", op.host_process, op.content, op.logical_time, file = outputfile)
                elif op.operation_type == "sent":
                    print("sent", op.host_process, op.content, op.target_process, op.logical_time, file = outputfile)
                elif op.operation_type == "recv":
                    print("received", op.host_process, op.content, op.target_process, op.logical_time, file = outputfile)
                else:
                    # shit went wrong badly for this to happen, mtx msgs should NEVER turn up in a mutex block
                    print("Tried to write a mtx_msg to file")

                    

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
    def __init__(self, operation_type, host_process, content, logical_time, mutex, target_process = None):
        self.operation_type = operation_type
        self.host_process = host_process
        self.content = content
        self.logical_time = logical_time
        self.target_process = target_process
        self.mutex = mutex

    def print_operation(self):
        """
        Prints operation to the file defined in outputfile
        Prints error msg to console if trying to print mtx_msg
        """
        if self.operation_type == "print":
            print("printed", self.host_process, self.content, self.logical_time, file = outputfile)
        elif self.operation_type == "sent":
            print("sent", self.host_process, self.content, self.target_process, self.logical_time, file = outputfile)
        elif self.operation_type == "recv":
            print("received", self.host_process, self.content, self.target_process, self.logical_time, file = outputfile)
        else:
            print("Tried to write a mtx_msg to file")

    def print_op_console(self):
        """
        Prints operation to console
        Can print all operation_type
        """
        if self.operation_type == "print":
            print ("printed", self.host_process, self.content, self.logical_time) 
        elif self.operation_type == "sent":
            print ("sent", self.host_process, self.content, self.target_process, self.logical_time) 
        elif self.operation_type == "recv":
            print ("received", self.host_process, self.content, self.target_process, self.logical_time)
        else:
            print (self.operation_type, self.host_process, self.target_process, self.logical_time)
            
                 
def print_ordered_all_operations():
    i = 0
    # current_Lampard_value starts at two such that all ops with logical_time == 1 can be printed
    current_Lampard_value = 2
    #reset op counters
    for pro in processes.values():
        pro.operation_counter = 0

    max_ops = [len(ops) for pro in processes.values() for ops in pro.operations]     # find the lengths of the operations arrays of the processes

    while i < max_ops:
        i += 1

        # pro is the current process being executed
        for pro in processes.values():
            if i < len(pro.operations):

                op = pro.operations[pro.operation_counter]

                if op.logical_time < current_Lampard_value:

                    if type(op) is Mutex:
                        op.print_operation()
                        # update current_Lampard_value to logical_time of last operation in the mutex block
                        current_Lampard_value = max(current_Lampard_value, op.processes[-1].logical_time)
                        pro.operation_counter += 1

                    # print a single send, recv, print instruction print isn't strictly necessary in the below instruction, as print is always a mutex op
                    elif op.operation_type in ["send","recv","print"]:
                        op.print_operation()
                        op.print_op_console()
                        pro.operation_counter += 1
                        current_Lampard_value = max(current_Lampard_value, op.logical_time + 1)

                    # if dealing with mutex arbitration messages, increment op counter, print to console, and continue
                    elif op.operation_type in ["mtx_req_send" ,"mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]:
                        op.print_op_console()
                        pro.operation_counter += 1
                        current_Lampard_value = max(current_Lampard_value, op.logical_time + 1)


    close(outputfile)

           















