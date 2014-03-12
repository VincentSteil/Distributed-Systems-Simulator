#!/usr/bin/python
"""
Vincent Steil
s1008380
Distributed Systems Practical
Process.py
"""

class Process():
    """
    docstring for Process
    Contains a list of Operations and keeps track of local Lampard Clock Time
    """
    # dictionary of Processes
    # Processes do not need to be stored in an ordered fashion. This lets us store the key to each process in each operation for both host_process and target_process
    processes = {}
    current_process = None
    mutex = False


    def __init__(self, name):
        self.operations = []
        self.logical_time = 0

        self.name = name

class Operation():
    """
    docstring for Operation
    Operation datastructure
    Basic datastructure for the simulator
    """
    def __init__(self, operation_type, host_process, content, logical_time, target_process = None):
        self.operation_type = operation_type
        self.host_process = host_process
        self.content = content
        self.logical_time = logical_time
        self.target_process = target_process

    def print_operation(self):
        if self.operation_type == "print":
            print("printed", self.host_process, self.content, self.logical_time)
        elif self.operation_type == "sent":
            print("sent", self.host_process, self.content, self.target_process, self.logical_time)
        elif self.operation_type == "recv":
            print("received", self.host_process, self.content, self.target_process, self.logical_time)
            

class Mutex():
    """
    docstring for Mutex
    Mutex block datastructure
    Contains a list of Operations
    """
    def __init__(self):
        self.ops = []
        

                      


