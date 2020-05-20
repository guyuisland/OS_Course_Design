"""
author: Owen
Last modify: 2020/5/20
"""

import process_sim as ps

PCB_queue = []
# Notice: maybe should not call it a queue since it has no priority
waiting_processes = []
ready_queue = []


def choose_to_run(msg):
    """
    msg: self-defined class object / json, should include:
        1. msg time
        2. msg id
        3. schedule type(choose_to_run for this func)
        4. (Optional) pid of running process on CPU now
        5. (Optional) algorithm of scheduling
    """
    chosen_pid = 0

    for process in ready_queue:
        # use round robin algorithm to find the process
        chosen_pid = process.pid
        break

    ps.move_from_ready_to_running(chosen_pid, ready_queue, PCB_queue)

    # TODO: Send a msg to kernel, finish scheduling


def move_to_wait(msg):
    """
    Another solution:
    send a msg, ask the CPU to move the running process to waiting
    """
    ps.move_from_running_to_waiting(
        msg.pid, waiting_processes, ready_queue, PCB_queue)

    # TODO: Send a msg to kernel, finish scheduling

    if len(ready_queue):  # the ready queue is not empty
        # TODO: rewrite the msg
        choose_to_run(msg)


def move_to_ready(msg):
    ps.move_from_running_to_ready(msg.pid, ready_queue, PCB_queue)
    # TODO: Send a msg to kernel, finish scheduling


def terminate(msg):
    # TODO: modify a PCB status to terminated
    # TODO: Send a msg to kernel
    pass

