# A1 for COMPSCI340/SOFTENG370 2015
# Prepared by Robert Sheehan
# Modified by ...

# You are not allowed to use any sleep calls.

#Name: Allen Liu
#UPI:	946912774

from threading import Lock, Event
from process import State


class Dispatcher():
    """The dispatcher."""

    MAX_PROCESSES = 8

    def __init__(self):
        """Construct the dispatcher."""
        self.lock = Lock()
        self.processStack = []
        self.processList = []
        for i in range(self.MAX_PROCESSES):
            self.processList.append(False)

    def set_io_sys(self, io_sys):
        """Set the io subsystem."""
        self.io_sys = io_sys

    def add_process(self, process):
        """Add and start the process."""

        self.lock.acquire

        if self.processStack:
            self.processStack[-1].tos = False
        
        self.processStack.append(process)

        self.io_sys.allocate_window_to_process(process, len(self.processStack) - 1)
        
        self.lock.release

        process.start()


        
    def dispatch_next_process(self):
        """Dispatch the process at the top of the stack."""

        self.lock.acquire
        if self.processStack:
            self.processStack[-1].tos = True
            self.processStack[-1].event.set()
            self.processStack[-1].event.clear()
        self.lock.release

    def to_top(self, process):
        """Move the process to the top of the stack."""

        if len(self.processStack) > 1:
            self.pause_system()

            index = self.processStack.index(process)
            self.processStack.append(self.processStack.pop(index))
            self.io_sys.remove_window_from_process(process)



            for i in range(index, len(self.processStack) - 1):
                process_to_move = self.processStack[i]
                self.io_sys.move_process(process_to_move, i)

            self.io_sys.allocate_window_to_process(process, len(self.processStack) - 1)

            self.resume_system()



    def pause_system(self):
        """Pause the currently running process.
        As long as the dispatcher doesn't dispatch another process this
        effectively pauses the system.
        """
        if self.processStack:
            self.processStack[-1].tos = False

    def resume_system(self):
        """Resume running the system."""
        self.dispatch_next_process()

    def wait_until_finished(self):
        """Hang around until all runnable processes are finished."""
        while self.processStack:
            pass

    def proc_finished(self, process):
        """Receive notification that "proc" has finished.
        Only called from running processes.
        """
        process.tos = False

        self.lock.acquire

        self.processStack.pop()
        if self.processStack:

            self.dispatch_next_process()

        self.lock.release

        self.io_sys.remove_window_from_process(process)

    def proc_waiting(self, process):
        """Receive notification that process is waiting for input."""

        self.lock.acquire

        index = self.processList.index(False)

        self.io_sys.move_process(process, index)
        self.processList[index] = process

        self.processStack.pop()

        if self.processStack:
            self.dispatch_next_process()

        process.tos = False
        process.event.clear()
        process.event.wait()

        self.lock.release


    def process_with_id(self, id):
        """Return the process with the id."""

        for key in self.io_sys.process_window_box.keys():
            if key.id == id:
                return key
