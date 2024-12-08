import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import random

## Memory Block Information.
class MemoryBlock:
    colors = {
        "used": (107, 228, 56),     # green colour for thoes block which are use memory 
        "free": (255, 225, 0),      # yellow colour for thoes block which are not use for any memory
        "fit": (236, 100, 75)       # red colour for thoes block which are requested for memory by user
    }
    # self_os = this variable use for oprating system done memory allocation by it self
    def __init__(self_os, range, type="used"): 
        self_os.range = range
        self_os.type = type

    def space(self_os):
        return self_os.range[1] - self_os.range[0]

    def typeID(self_os):
        color_types = {"used": 0, "free": 1, "fit": 2}
        return color_types.get(self_os.type, 0)
   
    def draw(self_os, painter, x, y0, w, h_scale):
        y = y0 + h_scale * self_os.range[0]
        h = self_os.space() * h_scale

        # using colour for show bloack 
        gradient = QLinearGradient(x, y, x, y + h)
        color = self_os.colors[self_os.type]
        gradient.setColorAt(0.0, QColor(*color))
        painter.setBrush(gradient)
        painter.drawRect(int(x), int(y), int(w), int(h)) # use this for draw rectangle.

        # Display block and size
        size = f"{self_os.space()} MB"
        painter.drawText(int(x + 0.5*w - 15), int(y + 0.5 * h + 5), size)

        # Add block type label in the top-left corner
        lable = self_os.type.capitalize()
        painter.drawText(int(x + 5), int(y + 15),lable)

## Memory information.
class Memory:
    def __init__(self_os, total_memory, occu_memory, free_memory_block):
        self_os.total_memory = total_memory
        self_os.occu_memory = occu_memory
        self_os.free_memory_block = free_memory_block
        self_os.fit_blocks = []
        self_os.success = 0.0

    ## Copy the memory information.
    def copy(self_os):
        return Memory(self_os.total_memory, self_os.occu_memory, self_os.free_memory_block)

    ## Return the free spaces of the memory.
    def freeSpaces(self_os):
        return [free_block.space() for free_block in self_os.free_memory_block]

    ## Fit the requested memory blocks to the free spaces.
    def fit(self_os, memory_requests, fit_func):
        success, fit_blocks = fit_func(self_os.freeSpaces(), memory_requests)
        self_os.difine_fit_blocks(fit_blocks)
        self_os.success = success

    ## Set memory blocks to the free spaces.
    def difine_fit_blocks(self_os, fit_blocks):
        for i, fit_blocks_i in enumerate(fit_blocks):
            fit_address = self_os.free_memory_block[i].range[0]
            for fit_block in fit_blocks_i:
                block = MemoryBlock((fit_address, fit_address + fit_block), "fit")
                self_os.fit_blocks.append(block)
                fit_address += fit_block

    ## Paint override for the memory.
    def draw(self_os, painter, x, y, w, h):
        h_scale = h / float (self_os.total_memory)

        for memory_space in self_os.occu_memory:
            memory_space.draw(painter, x, y, w, h_scale)

        for memory_space in self_os.free_memory_block:
            memory_space.draw(painter, x, y, w, h_scale)

        for memory_space in self_os.fit_blocks:
            if memory_space is not None:
                memory_space.draw(painter, x, y, w, h_scale)

## Memory requests.
class Requests:
    def __init__(self_os, total_memory, memory_requests):
        self_os.total_memory = total_memory
        self_os.memory_requests = memory_requests

    ## Paint override for the requested memory blocks.
    def draw(self_os, painter, x, y, w, h):
        h_scale = h / float(self_os.total_memory)

        hi = 20
        for memory_request in self_os.memory_requests:
            memory_space = MemoryBlock((hi, hi + memory_request), "fit")
            memory_space.draw(painter, x, y, w,h_scale)
            hi += memory_request + 20

## user inputs for total memory size
class Memory_define:
    def __init__(self_os):
        self_os.total_memory = self_os.get_input("Memory Size", 1000)
        self_os.block_min = self_os.get_input("Memory Block Min", 50)
        self_os.block_max = self_os.get_input("Memory Block Min", self_os.total_memory)
        self_os.num_trials = self_os.get_input("Num Trials", 10)

    def get_input(self_os, label, default):
        while True:
            try:
                user_input = input(f"Enter {label} (default {default}): ")
                # If the user presses enter without input, use the default value
                if user_input == "":
                    return default
                # Convert the input to an integer
                user_value = int(user_input)
                return user_value
            except ValueError:
                print(f"Invalid input. Please enter an integer.")

# randome memory allocation
def random_Memory(total_memory, block_min ,block_max):
    memory_lists = []
    total = 0
    while total < total_memory:
        memory_lists.append(total)
        total += random.randint(block_min, block_max)

    memory_lists.append(total_memory)

    occu_memory = [MemoryBlock((memory_lists[i], memory_lists[i+1]), "used") for i in range(0, len(memory_lists) - 1, 2)]
    free_memory_block = [MemoryBlock((memory_lists[i], memory_lists[i+1]), "free") for i in range(1, len(memory_lists)-1, 2)]

    return Memory(total_memory, occu_memory, free_memory_block)

# get memory request for user
def getMemoryRequests(free_spaces):
    total_memory = 0.8 * np.sum(free_spaces)
    memory_requests = []
   
    while True:
        try:
            memory_request = float(input(f"Enter memory request: "))
            memory_requests.append(memory_request)
            continue_input = input("Do you want to add another memory request? (y/n): ").lower()
            if continue_input != 'y':
                break
       
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    return memory_requests

def commonFit(free_spaces, memory_requests, fit_func):
    fit_spaces = np.zeros(len(free_spaces))
    fit_blocks = [[] for i in range(len(free_spaces))]
    num_fitted = 0

    for memory_request in memory_requests:
        fitted = fit_func(free_spaces, memory_request, fit_spaces, fit_blocks)
        num_fitted += fitted

    success = num_fitted / float(len(memory_requests))
    return success, fit_blocks
    

## Fit algo. implementations
def firstFit_algo(free_spaces, memory_requests):
    def fit_func(free_spaces, memory_request, fit_spaces, fit_blocks):
        for i in range(len(free_spaces)):
            if fit_spaces[i] + memory_request < free_spaces[i]:
                fit_blocks[i].append(memory_request)
                fit_spaces[i] += memory_request
                return 1
        return 0
    
    return commonFit(free_spaces, memory_requests, fit_func)

def bestFit_algo(free_spaces, memory_requests):
    def fit_func(free_spaces, memory_request, fit_spaces, fit_blocks):
        free_min = 1000
        fit_id = -1
        for i in range(len(free_spaces)):
            if fit_spaces[i] + memory_request < free_spaces[i]:
                free_space = free_spaces[i] - (fit_spaces[i] + memory_request)
                if free_space < free_min:
                    free_min = free_space
                    fit_id = i
        if fit_id > -1:
            fit_blocks[fit_id].append(memory_request)
            fit_spaces[fit_id] += memory_request
            return 1
        return 0
    
    return commonFit(free_spaces, memory_requests, fit_func)

def worstFit_algo(free_spaces, memory_requests):
    def fit_func(free_spaces, memory_request, fit_spaces, fit_blocks):
        free_max = 0
        fit_id = -1
        for i in range(len(free_spaces)):
            if fit_spaces[i] + memory_request < free_spaces[i]:
                free_space = free_spaces[i] - (fit_spaces[i] + memory_request)
                if free_space > free_max:
                    free_max = free_space
                    fit_id = i

        if fit_id > -1:
            fit_blocks[fit_id].append(memory_request)
            fit_spaces[fit_id] += memory_request
            return 1
        return 0

    return commonFit(free_spaces, memory_requests, fit_func)


# memory allocation simulator.
class SimulatorView(QWidget):

    def __init__(self_os, setting, parent=None):
        super(SimulatorView, self_os).__init__(parent)
        self_os._setting = setting
        self_os.simulation()

    ## Paint override: MemoryRequests, 3 Memory objects (First-Fit, Best-Fit, Worst-Fit).
    def paintEvent(self_os,event):
        painter = QPainter(self_os)
        painter.begin(self_os)

        h = self_os.height() - 40
        w = self_os.width() // 5  
        painter.drawText(20, 20, "Memory Requests")
        self_os._requests.draw(painter, 20, 30, w, h)

        x = 40 + w
        labels = ["First-Fit", "Best-Fit", "Worst-Fit"]

        for label, memory in zip(labels, self_os._memories):
            painter.drawText(x, 20, label + ": %s%%" % round(100 * memory.success, 1))
            memory.draw(painter, x, 30, w, h)
            x += w + 20

        painter.end()


    ## Simulate with requested memory
    def simulation(self_os):
        total_memory = self_os._setting.total_memory
        block_min = self_os._setting.block_min
        block_max = self_os._setting.block_max
        memory = random_Memory(total_memory, block_min, block_max)
        self_os._memories = [memory, memory.copy(), memory.copy()]

        free_spaces = memory.freeSpaces()
        memory_requests = getMemoryRequests(free_spaces)
        self_os._requests = Requests(total_memory, memory_requests)

        fits = [firstFit_algo, bestFit_algo, worstFit_algo]
        for memory, fit_func in zip(self_os._memories, fits):
            memory.fit(memory_requests, fit_func)


## display result
class MainWindow(QMainWindow):
    def __init__(self_os):
        super(MainWindow, self_os).__init__()
        self_os.setWindowTitle("Memory Allocation: First-Fit , Best-Fit, Worst-Fit")
        self_os._setting = Memory_define()

        view = SimulatorView(self_os._setting)

        self_os.setCentralWidget(view)
        self_os.show()

    def event_end(self_os, event):
        QApplication.closeAllWindows()
        return QMainWindow.event_end(self_os, event)

## Main function to show main window.
def main():
    app = QApplication(sys.argv)
    mainscreen = MainWindow()
    mainscreen.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()