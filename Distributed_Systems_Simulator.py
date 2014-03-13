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

            elif (line[0] == "begin" and line[1] == "mutex"):
                Process.mutex_block = True

            elif (line[0] == "end" and line[1] == "mutex"):
                Process.mutex_block = False

            elif line[0] == "send":
                if(Process.mutex_block):              
                    Process.processes[Process.current_process].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[2], logical_time = Process.processes[Process.current_process].logical_time, target_process = line[1], mutex = True))
                else:
                    Process.processes[Process.current_process].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[2], logical_time = Process.processes[Process.current_process].logical_time, target_process = line[1], mutex = False))

            elif line[0] == "recv":
                if(Process.mutex_block):              
                    Process.processes[Process.current_process].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[2], logical_time = Process.processes[Process.current_process].logical_time, mutex = True, target_process = line[1],))
                else:
                    Process.processes[Process.current_process].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[2], logical_time = Process.processes[Process.current_process].logical_time, mutex = False, target_process = line[1]))           

            elif line[0] == "print":
                # print operation is always a single process mutex block
                Process.processes[Process.current_process].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process], content = line[1], logical_time = Process.processes[Process.current_process].logical_time, mutex = True))


def run_simulator():
    i = 0
    max_ops = [len(ops) for pro in Process.processes.values() for ops in pro.operations]     # find the lengths of the operations arrays of the processes

    while i < max(max_ops):      # iterate until the end of each process is found
       i += 1

       # pro is the current process being executed
       for pro in Process.processes.values():
            # don't run if there are no more operations
            max_ops = max(max_ops, len(pro.operations))
            if i < len(pro.operations):
                pro.logical_time += 1
                if pro.status == held:
                    # if the status is held, the process is in a mutex block and can do whatever it wants
                    if pro.operations[pro.operation_counter].operation_type in ["send","recv", "print"]:
                        run_basic_operation(pro)
                    # mtx_req_send is dealt with in the above case, that means we're left dealing with mtx_req_recv, mtx_req_grant_recv, and mtx_req_grant_send  
                    elif pro.operations[pro.operation_counter].operation_type in ["mtx_req_recv", "mtx_req_grant_recv", "mtx_req_grant_send"]:
                        run_mtx_operation(pro)

                elif pro.operations[pro.operation_counter].mutex == True and pro.status == released:
                    pro.status = wanted
                    # store Lampard clock value of the initial request 
                    # we can't actually multicast, so we store the intial Lampard clock value of the multicast
                    pro.mtx_req_send_time = pro.logical_time    

                    # generate the mtx request msgs by adding them to the current front of the requesting process
                    for pro_multicast in Process.processes.values():
                        if pro_multicast.name != pro.name:
                            pro.insert(pro.operation_counter, Operation(operation_type = "mtx_req_send", host_process = pro.name, content = "mtx_req_send", logical_time = pro.logical_time, mutex = False, target_process = pro_multicast.name))

                    # work off the first mtx request and add it to the relevant process
                    assert pro.operations[operation_counter].target_process.operation_type == "mtx_req_send"
                    Process.processes[pro.operations[operation_counter].target_process] = recv_mtx_pro          # this is the first target of the mtx_seq_send operations just added
                    # queue send the first mtx_req msg(and thus queue the first  mtx_req_recv msg on the target process)
                    queue_mtx_req_recv(pro,recv_mtx_pro)

                elif pro.operations[pro.operation_counter].mutex == False and pro.status == released:
                    if pro.operations[pro.operation_counter].operation_type in ["send","recv"]:
                        run_basic_operation(pro)
                    # mtx_req_send is dealt with in the above case, that means we're left dealing with mtx_req_recv, mtx_req_grant_recv, and mtx_req_grant_send  
                    elif pro.operations[pro.operation_counter].operation_type in ["mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]:
                        run_mtx_operation(pro)

                elif pro.status == wanted:
                    assert pro.operations[pro.operation_counter].mutex == False
                    if pro.operations[pro.operation_counter].operation_type in ["mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]:
                        run_mtx_operation(pro)
                    elif pro.operations[pro.operation_counter].operation_type == "mtx_req_send":
                        assert pro.operations[operation_counter].target_process.operation_type == "mtx_req_send"
                        Process.processes[pro.operations[operation_counter].target_process] = recv_mtx_pro  
                        queue_mtx_req_recv(pro, recv_mtx_pro)





def run_mtx_operation(host_pro):
    op = host_pro.operations[host_pro.operation_counter]
    assert op.operation_type in ["mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]

    if op.status == held and op.mutex == False:
        op.status = released

    if op.operation_type == "mtx_req_recv":
        # the recv msg has already been slotted into the correct place, thus we can queue the mtx_req_grant_send msg in the front, as
        host_pro.logical_time = max(host_pro.logical_time, op.logical_time) 
        host_pro.operations.insert(host_pro.operation_counter, Operation(operation_type = "mtx_req_grant_send", host_process = host_pro.name, content = "mtx_req_grant_send", logical_time = host_pro.logical_time, mutex = False, target_process = op.target_process))

    elif op.operation_type == "mtx_req_grant_send":
        op.target_process.operations.insert(op.target_process.operations.operation_counter, Operation(operation_type = "mtx_req_grant_recv", host_process = target_pro.name, content = "mtx_req_grant_recv", logical_time = host_pro.logical_time, mutex = False, target_process = op.target_process))

    elif op.operation_type == "mtx_req_grant_recv":
        host_pro.logical_time = max(host_pro.logical_time, op.logical_time) 
        host_pro.mtx_req_grant_recv_set.add(op.target_process)
        if len(set(Process.processes).difference(host_pro.mtx_req_grant_recv_set)) < 2:
            host_pro.state = held
            # empty set of request granters
            for ID in host_pro.mtx_req_grant_recv_set
                host_pro.mtx_req_grant_recv_set.remove(ID)


    host_pro.operation_counter += 1

def run_basic_operation(host_pro):
    """
    Run a single operation (send, print, recv) from host_pro
    """
    # current operation
    op = host_pro.operations[host_pro.operation_counter]
    assert op.operation_type in ["send","recv","print"]

    if op.status == held and op.mutex == False:
        op.status = released

    if op.operation_type == "send":
        op.logical_time = host_pro.logical_time
        # the list of send messages at the receiver is used to transmit the timestamps, as those were just dummy values when first reading the data in
        Process.processes[op.target_process].received_messages[(host_pro.name, op.content)].append(host_pro.logical_time)

    elif op.operation_type == "print":
        op.logical_time = host_pro.logical_time

    elif op.operation_type == "recv":
        if (op.target_process, op.content) in host_pro.received_messages:
            if len(host_pro.received_messages[(op.target_process, op.content)]) > 0:
                timestamp = max(host_pro.logical_time, min(host_pro.received_messages[(op.target_process, op.content)]))
                op.logical_time = timestamp
                host_pro.logical_time = timestamp
                host_pro.received_messages.remove(min(host_pro.received_messages[(op.target_process, op.content)]))

        else:
            # if the message hasn't been sent yet, it's not in host_pro.received_messages, so we have a round of do nothing until the process sends the msg
            # decrement logical_time, as we do nothing, yet increment above
            host_pro.logical_time -= 1
            host_pro.operation_counter -= 1



    host_pro.operation_counter += 1



# call this function when you need to queue a mtx_req_recv message     
def queue_mtx_req_recv(host_pro, target_pro):
    """
    This function queues a mtx_req_recv message and is called when dealing with a mtx_req_send message at the host processor
    This function DOES NOT !! send out the mtx_req_grant message by queueing that with the requesting process. That is done when the mtx_req_grant sender is actually the operating host.
    """
    # just add it if the receiving process is not in a mutex block
    if target_pro.status == released
        target_pro.operations.insert(target_pro.operation_counter, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name))

    # find the end of the mutex block and mutex request queue and add the mtx_req_recv message to the end of it
    elif target_pro.status == held 
        mutex_offset = 1

        while target_pro.operations[target_pro.operation_counter + mutex_offset].mutex == True or target_pro.operations[target_pro.operation_counter + mutex_offset].operation_type in ["mtx_req_recv", "mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]:
            mutex_offset += 1

        target_pro.operations.insert(target_pro.operation_counter + mutex_offset, Operation(operation_type = "mtx_req_recv", host_process = recv_target_promtx_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name))

    elif target_pro.status == wanted:
        if target_pro.mtx_req_send_time < host_pro.mtx_req_send_time:
            mutex_offset = 1
             # find the end of the mutex block and mutex request queue and add the mtx_req_recv message to the end of it
            while target_pro.operations[target_pro.operation_counter + mutex_offset].mutex == True or target_pro.operations[target_pro.operation_counter + mutex_offset].operation_type in ["mtx_req_recv",  "mtx_req_send", "mtx_req_grant"]:
                mutex_offset += 1
            target_pro.operations.insert(target_pro.operation_counter + mutex_offset, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name))
        
        elif target_pro.mtx_req_send_time > host_pro.mtx_req_send_time:
            target_pro.operations.insert(target_pro.operation_counter, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name))

        elif target_pro.name < host_pro.name:
            mutex_offset = 1
             # find the end of the mutex block and mutex request queue and add the mtx_req_recv message to the end of it
            while target_pro.operations[target_pro.operation_counter + mutex_offset].mutex == True or target_pro.operations[target_pro.operation_counter + mutex_offset].operation_type in ["mtx_req_recv",  "mtx_req_send", "mtx_req_grant"]:
                mutex_offset += 1
            target_pro.operations.insert(target_pro.operation_counter + mutex_offset, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name))
        
        else:
             target_pro.operations.insert(target_pro.operation_counter, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name))
    
    # increment operation counter, as we did work
    host_pro.operation_counter += 1

 









          