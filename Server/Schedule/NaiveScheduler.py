import sys
from Device.Device_Base import Device
from Schedule.Job import Job
from typing import List
from Schedule.Scheduler import Scheduler

# a job made for testing, which can be stopped by the scheduler
class testJob(Job):
    def __init__(self, duration: int|float, draw: int|float, deadline: int|float, start: int|float, name: str):
        super().__init__(Device(name,"test","0",0), duration, draw, deadline, start, [], name, self.start)

    def start(self, timestamp: int|float):
        self.running = True
        self.started = timestamp
    
    def stop(self):
        self.running = False
        self.finished = True
    
class naiveScheduler(Scheduler):
    def __init__(self, jobs: List[Job], start_threshold: int|float, diff_threshold: int|float) -> None:
        super().__init__()
        self.jobs = jobs
        self.start_threshold = start_threshold
        self.diff_threshold = diff_threshold

    def run(self, timeStamp: int|float, currentProduction: int|float) -> List[Job]:
        """
        Runs the scheduling with the given time and production,
        Returns a list of the jobs started
        """
        remainingProduction = currentProduction
        startedJobs = []
        availableJobs = []

        for job in self.jobs:
            # stopping finished devices
            if job.running and job.started + job.duration <= timeStamp:
                job.stop()
            
            # keeping count of running devices
            elif job.running:
                remainingProduction -= job.draw

            # Inforcing jobs before the deadline is reached
            elif timeStamp >= job.deadline - job.duration and not job.finished and job.deadline != 0:
                startedJobs.append(job)
                job.deviceCommand(timeStamp)
                remainingProduction -= job.draw
            
            elif not job.finished and job.withinInterval(timeStamp):
                availableJobs.append(job)
    
        if remainingProduction < self.start_threshold:
            return startedJobs
        
        for _ in availableJobs:
            if remainingProduction <= 0:
                break
            
            job = min(availableJobs, key=lambda dev: abs(dev.draw - remainingProduction))

            # stopping too expensive jobs
            if job.draw - remainingProduction > self.diff_threshold:
                availableJobs.remove(job)
                continue

            startedJobs.append(job)
            job.deviceCommand(timeStamp)
            remainingProduction -= job.draw
            availableJobs.remove(job)
        return startedJobs

if __name__=="__main__":
    print("This is a module, no run run")

