import sys
from Device.Device_Base import Device
from typing import Callable
from abc import abstractclassmethod

class Job():
    
    device = None   #The device to be run
    name = ""
    duration = 0        #how long it should run
    draw = 0            #how much energy it consumes
    deadline = 0        #When it should be done
    earliestStart = 0   #when it can at the earliest be started

    # a list of days to run (currently list of bool but it has not yet been decided how it should be represented)
    
    deviceCommand = (lambda: print("not implemented")) #The command which is used to start the device

    started = 0         #time of when it was started
    running = False     #is it currently running
    finished = False    #is the job finished running

    def __init__(self, device: Device, duration: int|float, draw: int|float, deadline: int|float, earliestStart: int|float, daysToRun: list, name: str, command: Callable[[int|float],None]):
        self.device = device
        self.duration = duration
        self.draw = draw
        self.deadline = deadline
        self.earliestStart = earliestStart
        self.daysToRun = daysToRun
        self.started = 0
        self.name = name
        self.deviceCommand=command
        self.running = False
        self.finished = False

    def withinInterval(self,i):
        if self.deadline == 0: 
            return i >=  self.earliestStart
        return i >= self.earliestStart and i <= self.deadline

    def stop(self):
        self.running = False
        self.finished = True
