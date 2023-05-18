from abc import abstractclassmethod
from typing import List
from Schedule.Job import Job

class Scheduler:
    jobs:List[Job]
    
    @abstractclassmethod
    def run(self, timeStamp: int|float, currentProd: int|float) -> List[Job]:
        pass
