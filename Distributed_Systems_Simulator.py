#!/usr/bin/python
"""
Vincent Steil
s1008380
Distributed Systems Practical
Distributed_Systems_Simulator.py
Pydoc:
pydoc -w Distributed_Systems_Simulator

"""
import sys, getopt
from Process_DS import Process 
from Process_DS import Operation
from Process_DS import Mutex
import Process_DS

def set_IO(argv):
    """
    sets the IO strings from command line arguments
    """
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print 'Input file is "', inputfile
    print 'Output file is "', outputfile
    return [inputfile, outputfile]


def read_simulator_input(infile):
    """
    docstring for read_simulator_input
    Read in all the data from the file and store the parsed lines as Operation and Mutex it in the Process dictionary defined in Process.py
    """


    with open(infile, 'r') as f:
        print("Starting to read in data")
        for line in f:
            line = line.split()
            if len(line) > 0:
                if (line[0] == "begin" and line[1] == "process"):
                    Process.processes[line[2]] = Process(line[2])
                    Process.current_process = line[2]     

                elif (line[0] == "begin" and line[1] == "mutex"):
                    Process.mutex_block = True
                    Process.processes[Process.current_process].operations.append(Mutex())

                elif (line[0] == "end" and line[1] == "mutex"):
                    Process.mutex_block = False

                elif line[0] == "send":
                    if(Process.mutex_block):
                        assert isinstance((Process.processes[Process.current_process].operations[-1]), Mutex)               
                        Process.processes[Process.current_process].operations[-1].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[2], logical_time = Process.processes[Process.current_process].logical_time, target_process = line[1], mutex = True))
                    else:
                        Process.processes[Process.current_process].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[2], logical_time = Process.processes[Process.current_process].logical_time, target_process = line[1], mutex = False))

                elif line[0] == "recv":
                    if(Process.mutex_block):
                        assert isinstance((Process.processes[Process.current_process].operations[-1]), Mutex)              
                        Process.processes[Process.current_process].operations[-1].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[2], logical_time = Process.processes[Process.current_process].logical_time, mutex = True, target_process = line[1],))
                    else:
                        Process.processes[Process.current_process].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[2], logical_time = Process.processes[Process.current_process].logical_time, mutex = False, target_process = line[1]))           

                elif line[0] == "print":
                    if(Process.mutex_block):
                        assert isinstance((Process.processes[Process.current_process].operations[-1]), Mutex)
                        Process.processes[Process.current_process].operations[-1].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[1], logical_time = Process.processes[Process.current_process].logical_time, mutex = True))
                    else:
                        Process.processes[Process.current_process].operations.append(Mutex())
                        # print operation is always a single process mutex block
                        assert isinstance((Process.processes[Process.current_process].operations[-1]), Mutex)
                        Process.processes[Process.current_process].operations[-1].operations.append(Operation(operation_type = line[0], host_process = Process.processes[Process.current_process].name, content = line[1], logical_time = Process.processes[Process.current_process].logical_time, mutex = True))
                else:
                    pass

        print("Finished reading in data")

def run_simulator():
    print("Starting simulator run")
    no_more_ops = False     # find the lengths of the operations arrays of the Process.processes
    i = 0
    while not no_more_ops:    # iterate until the end of each process is found
        # this flag is set to false the moment a process is actually still running 
        no_more_ops = True
        # pro is the current process being executed
        for pro in Process.processes.values():
            # don't run if there are no more operations
            if pro.operation_counter < len(pro.operations):
                pro.logical_time += 1
                no_more_ops = False
                op = pro.operations[pro.operation_counter]
                # Process.held status
                if pro.status == Process.held:
                    # non-consecutive mutex block
                    if not isinstance(op, Mutex):
                        # set status to Process.released if we try to execute a non-mutex block while in Process.held state 
                        if op.operation_type in ["send","recv"]:
                            run_basic_operation(pro)
                        # mtx_req_send is dealt with in the above case, that means we're left dealing with mtx_req_recv, mtx_req_grant_recv, and mtx_req_grant_send  
                        elif op.operation_type in ["mtx_req_recv", "mtx_req_grant_recv", "mtx_req_grant_send"]:
                            run_mtx_operation(pro)
                    # mutex block
                    else:
                        assert isinstance(op, Mutex)
                        # if the status is Process.held, the process is in a mutex block and can do whatever it wants
                        if op.operations[op.mutex_operation_offset].operation_type in ["send","recv", "print"]:
                            run_basic_operation(pro)
                        # mtx_req_send is dealt with in the above case, that means we're left dealing with mtx_req_recv, mtx_req_grant_recv, and mtx_req_grant_send  
                        else:
                            print("Non send, recv, print operation found in mutex block")


                elif isinstance(op, Mutex) and pro.status == Process.released:
                    pro.status = Process.wanted
                    # store Lampard clock value of the initial request 
                    # we can't actually multicast, so we store the intial Lampard clock value of the multicast
                    pro.mtx_req_send_time = pro.logical_time    

                    # generate the mtx request msgs by adding them to the current front of the requesting process
                    for pro_multicast in Process.processes.values():
                        if pro_multicast.name != pro.name:
                            pro.operations.insert(pro.operation_counter, Operation(operation_type = "mtx_req_send", host_process = pro.name, content = "mtx_req_send", logical_time = pro.logical_time, mutex = False, target_process = pro_multicast.name))

                    # work off the first mtx request and add it to the relevant process
                    assert pro.operations[pro.operation_counter].operation_type == "mtx_req_send"
                    recv_mtx_pro = Process.processes[pro.operations[pro.operation_counter].target_process]          # this is the first target of the mtx_seq_send operations just added
                    # queue send the first mtx_req msg(and thus queue the first  mtx_req_recv msg on the target process)
                    queue_mtx_req_recv(pro)

                elif (not isinstance(op, Mutex)) and pro.status == Process.released:
                    if pro.operations[pro.operation_counter].operation_type in ["send","recv"]:
                        run_basic_operation(pro)
                    # mtx_req_send is dealt with in the above case, that means we're left dealing with mtx_req_recv, mtx_req_grant_recv, and mtx_req_grant_send  
                    elif pro.operations[pro.operation_counter].operation_type in ["mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]:
                        run_mtx_operation(pro)

                elif pro.status == Process.wanted:
                    # do nothing, if we're still waiting for confirmation msgs
                    # decrement pro.logical_time to account for automatic increment
                    if isinstance(op, Mutex):
                        pro.logical_time -= 1
                    # work off mtx msgs
                    else:
                        if pro.operations[pro.operation_counter].operation_type in ["mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]:
                            run_mtx_operation(pro)
                        elif pro.operations[pro.operation_counter].operation_type == "mtx_req_send":
                            assert pro.operations[pro.operation_counter].operation_type == "mtx_req_send"
                            queue_mtx_req_recv(pro)   

    print("Finished simulator run")




def run_mtx_operation(host_pro):
    op = host_pro.operations[host_pro.operation_counter]
    target_pro = Process.processes[op.target_process]
    # op should not be a mutex block, as mtx msgs can not be in mutex blocks
    assert not isinstance(op, Mutex)
    assert op.operation_type in ["mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]

    if op.operation_type == "mtx_req_recv":
        # the recv msg has already been slotted into the correct place, thus we can queue the mtx_req_grant_send msg in the front, as
        timestamp = max(host_pro.logical_time, op.logical_time + 1) 
        host_pro.logical_time = timestamp
        op.logical_time = timestamp

        host_pro.operations.insert(host_pro.operation_counter + 1, Operation(operation_type = "mtx_req_grant_send", host_process = host_pro.name, content = "mtx_req_grant_send", logical_time = host_pro.logical_time, mutex = False, target_process = op.target_process))

    elif op.operation_type == "mtx_req_grant_send":
        op.logical_time = host_pro.logical_time
        target_pro.operations.insert(target_pro.operation_counter, Operation(operation_type = "mtx_req_grant_recv", host_process = target_pro.name, content = "mtx_req_grant_recv", logical_time = host_pro.logical_time, mutex = False, target_process = op.host_process))

    elif op.operation_type == "mtx_req_grant_recv":

        timestamp = max(host_pro.logical_time, op.logical_time + 1) 
        host_pro.logical_time = timestamp
        op.logical_time = timestamp

        host_pro.mtx_req_grant_recv_set.add(op.target_process)
        if len(set(Process.processes).difference(host_pro.mtx_req_grant_recv_set)) == 1:
            host_pro.status = Process.held
            # empty set of request granters
            host_pro.mtx_req_grant_recv_set = set()


    host_pro.operation_counter += 1

def run_basic_operation(host_pro):
    """
    Run a single operation (send, recv, print) from host_pro
    """

    # current operation
    op = host_pro.operations[host_pro.operation_counter] 
    # for Mutex blocks
    if isinstance(op, Mutex):
        mtx = host_pro.operations[host_pro.operation_counter]
        op = mtx.operations[op.mutex_operation_offset]
        if (mtx.mutex_operation_offset < len(mtx.operations)):
            if op.operation_type == "send":
                op.logical_time = host_pro.logical_time
                # the list of send messages at the receiver is used to transmit the timestamps, as those were just dummy values when first reading the data in
                if (host_pro.name, op.content) in Process.processes[op.target_process].received_messages:
                    Process.processes[op.target_process].received_messages[(host_pro.name, op.content)].append(host_pro.logical_time)
                else:
                    Process.processes[op.target_process].received_messages[(host_pro.name, op.content)] = [host_pro.logical_time]
                mtx.mutex_operation_offset += 1

            elif op.operation_type == "recv":
                if (op.target_process, op.content) in host_pro.received_messages:
                    if len(host_pro.received_messages[(op.target_process, op.content)]) > 0:

                        timestamp = max(host_pro.logical_time, min(host_pro.received_messages[(op.target_process, op.content)]) + 1)
                        op.logical_time = timestamp
                        host_pro.logical_time = timestamp

                        host_pro.received_messages[(op.target_process, op.content)].remove(min(host_pro.received_messages[(op.target_process, op.content)]))
                        mtx.mutex_operation_offset += 1

                else:
                    # if the message hasn't been sent yet, it's not in host_pro.received_messages, so we have a round of do nothing until the process sends the msg
                    # decrement logical_time, as we do nothing, yet increment above
                    host_pro.logical_time -= 1

            elif op.operation_type == "print":
                op.logical_time = host_pro.logical_time
                mtx.mutex_operation_offset += 1

        # else not used, as we want to update the process op counter without delay so that we can get out of the mutex block
        if (mtx.mutex_operation_offset >= len(mtx.operations)):
            host_pro.operation_counter += 1
            host_pro.status = Process.released


    # non Mutex operation
    else:   
        if op.operation_type == "send":
            op.logical_time = host_pro.logical_time
            # the list of send messages at the receiver is used to transmit the timestamps, as those were just dummy values when first reading the data in
            if (host_pro.name, op.content) in Process.processes[op.target_process].received_messages:
                Process.processes[op.target_process].received_messages[(host_pro.name, op.content)].append(host_pro.logical_time)
            else:
                Process.processes[op.target_process].received_messages[(host_pro.name, op.content)] = [host_pro.logical_time]
            host_pro.operation_counter += 1

        elif op.operation_type == "recv":
            if (op.target_process, op.content) in host_pro.received_messages:
                if len(host_pro.received_messages[(op.target_process, op.content)]) > 0:

                    timestamp = max(host_pro.logical_time, min(host_pro.received_messages[(op.target_process, op.content)]) + 1)
                    op.logical_time = timestamp
                    host_pro.logical_time = timestamp

                    host_pro.received_messages[(op.target_process, op.content)].remove(min(host_pro.received_messages[(op.target_process, op.content)]))
                    host_pro.operation_counter += 1

            else:
                # if the message hasn't been sent yet, it's not in host_pro.received_messages, so we have a round of do nothing until the process sends the msg
                # decrement logical_time, as we do nothing, yet increment above
                host_pro.logical_time -= 1



    



# call this function when you need to queue a mtx_req_recv message     
def queue_mtx_req_recv(host_pro):
    """
    This function queues a mtx_req_recv message and is called when dealing with a mtx_req_send message at the host processor
    This function DOES NOT !! send out the mtx_req_grant message by queueing that with the requesting process. That is done when the mtx_req_grant sender is actually the operating host.
    """

    op = host_pro.operations[host_pro.operation_counter]
    target_pro = Process.processes[op.target_process]

    assert not isinstance(op, Mutex)
    op.logical_time = host_pro.logical_time
    # just add it if the receiving process is not in a mutex block
    if target_pro.status == Process.released:
        target_pro.operations.insert(target_pro.operation_counter, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name, multicast_logical_time = host_pro.mtx_req_send_time))

    # find the end of the mutex block and mutex request queue and add the mtx_req_recv message to the end of it
    elif target_pro.status == Process.held: 
        mutex_offset = 0

        while isinstance((target_pro.operations[target_pro.operation_counter + mutex_offset]), Mutex) or target_pro.operations[target_pro.operation_counter + mutex_offset].operation_type in ["mtx_req_recv", "mtx_req_recv", "mtx_req_grant_send", "mtx_req_grant_recv"]:
            if mutex_offset >= len(target_pro.operations) or isinstance((target_pro.operations[target_pro.operation_counter + mutex_offset]), Mutex):
                break
            mutex_offset += 1
        target_pro.operations.insert(target_pro.operation_counter + mutex_offset, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name, multicast_logical_time = host_pro.mtx_req_send_time))

    elif target_pro.status == Process.wanted:
        # target_pro wins, add to end of mutex block, mtx msg queue
        if target_pro.mtx_req_send_time < host_pro.mtx_req_send_time:
            mutex_offset = 0
             # find the end of the mutex block and mutex request queue and add the mtx_req_recv message to the end of it
            while isinstance((target_pro.operations[target_pro.operation_counter + mutex_offset]), Mutex) or target_pro.operations[target_pro.operation_counter + mutex_offset].operation_type in ["mtx_req_recv",  "mtx_req_send", "mtx_req_grant"]:
                if mutex_offset >= len(target_pro.operations) or isinstance((target_pro.operations[target_pro.operation_counter + mutex_offset]), Mutex):
                    break
                mutex_offset += 1

            target_pro.operations.insert(target_pro.operation_counter + mutex_offset, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name, multicast_logical_time = host_pro.mtx_req_send_time))
        
        # host_pro wins, add msg to beginning of current target_pro operations
        elif target_pro.mtx_req_send_time > host_pro.mtx_req_send_time:
            target_pro.operations.insert(target_pro.operation_counter, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name, multicast_logical_time = host_pro.mtx_req_send_time))

        # target_pro wins tie breaker, add to end of mutex block, mtx msg queue
        elif target_pro.name < host_pro.name:
            mutex_offset = 0
             # find the end of the mutex block and mutex request queue and add the mtx_req_recv message to the end of it
            while isinstance((target_pro.operations[target_pro.operation_counter + mutex_offset]), Mutex) or target_pro.operations[target_pro.operation_counter + mutex_offset].operation_type in ["mtx_req_recv",  "mtx_req_send", "mtx_req_grant"]:
                if mutex_offset >= len(target_pro.operations) or isinstance((target_pro.operations[target_pro.operation_counter + mutex_offset]), Mutex):
                    break 
                mutex_offset += 1               
            target_pro.operations.insert(target_pro.operation_counter + mutex_offset, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name, multicast_logical_time = host_pro.mtx_req_send_time))
        
        # host_pro wins tie breaker, add msg to beginning of current target_pro operations
        else:
             target_pro.operations.insert(target_pro.operation_counter, Operation(operation_type = "mtx_req_recv", host_process = target_pro.name, content = "mtx_req_recv", logical_time = host_pro.logical_time, mutex = False, target_process = host_pro.name, multicast_logical_time = host_pro.mtx_req_send_time))
    
    # increment operation counter, as we did work
    host_pro.operation_counter += 1

 









          