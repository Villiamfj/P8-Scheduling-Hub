from Schedule.Scheduler import Scheduler
from Production.Prod_device import Prod_device
import time
from datetime import datetime
import threading

def loop(scheduler: Scheduler,production: Prod_device):
    # time update
    i = datetime.now().timestamp()
    # prod update
    power = production.get_power()
    # schedule
    started = scheduler.run(i,power)
    names = [x.name for x in started]
    print(names,power,datetime.fromtimestamp(i))

# inspired by https://gist.github.com/stamat/5371218
def set_interval(func, sec, args):
    def func_wrapper():
        set_interval(func, sec, args) 
        func(*args)  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t