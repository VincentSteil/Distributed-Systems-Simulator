#!/usr/bin/python
"""
Vincent Steil
s1008380
Distributed Systems Practical
Process.py
"""

class Process(object):
    """
    docstring for Process
    
    """
    current_process = 0

    def __init__(self, name):
        operations = []
        logical_time = 0

        self.name = name

class Operation(object):
    """
    docstring for Operation
    Operation datastructure
    Basic datastructure for the simulator
    """
    def __init__(self, operation_type, host_process, message, logical_time, target_process = None):
        self.operation_type = operation_type
        self.host_process = host_process
        self.message = message
        self.logical_time = logical_time
        self.target_process = target_process

class Mutex(object):
    """
    docstring for Mutex
    Mutex block datastructure
    Contains a list of Operations
    """
    def __init__(self):
        ops = []
        

                      


