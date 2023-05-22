from Schedule.Scheduler import Scheduler
from typing import List
from Schedule.Job import Job
import keras
from datetime import datetime
from Production.Prod_device import Prod_device
import numpy as np
from Schedule.NaiveScheduler import naiveScheduler
import math as m


class Forecaster:
    def __init__(self, modelLocation: str, expectedLen: int, timeLen: float) -> None:
        self.model = keras.models.load_model(modelLocation)
        self.forecastLen = expectedLen
        self.timeLen = timeLen

    def get(self,input):
        if len(input[0]) != self.forecastLen:
            # trying to convert input to desired length
            input = input[0]
            ratio = len(input) / self.forecastLen
            if isinstance(ratio,int):
                raise Exception("Forecaster does not support that length of input",len(input))
            
            ratio = int(ratio)
            r = [] # the reduced / compressed set
            for i in range(0,len(input),ratio):
                r.append(sum(input[i:i+ratio]) / ratio)
            input = np.array([r])
        
        normalized, min, max = self.normalize_time_series(input)
        return self.denormalize_time_series(self.model(normalized)[0],min,max)
    
    def normalize_time_series(self,time_series):
        min_val = np.min(time_series)
        max_val = np.max(time_series)
        normalized_time_series = (time_series - min_val) / (max_val - min_val)
        return normalized_time_series, min_val, max_val

    def denormalize_time_series(self,normalized_time_series, min_val, max_val):
        time_series = normalized_time_series * (max_val - min_val) + min_val
        return time_series
    
class ForecastScheduler(Scheduler):
    def __init__(self, jobs: List[Job], 
                 start_threshold: int|float, 
                 diff_threshold: int|float, 
                 prod_device: Prod_device, 
                 timeBetweenForecast: int|float, 
                 stepsInADay: int,
                 modelLocation: str,
                 forecastTimeLen: float) -> None:
        super().__init__()
        self.jobs = jobs
        self.start_threshold = start_threshold
        self.diff_threshold = diff_threshold
        self.prod_device = prod_device

        # The forecaster returns 48 points in a day
        self.forecaster = Forecaster(modelLocation, 48, forecastTimeLen)
        self.naive = naiveScheduler(self.jobs, start_threshold, diff_threshold)
        
        self.stepsInADay = stepsInADay
        self.timeToForecast = timeBetweenForecast

        self.jobsSch = {}
        self.updateForecast(0)
    
    def updateForecast(self, timestamp):
        history = self.prod_device.get_history()
        if len(history) < self.stepsInADay:
            self.forecast = []
            self.forecastDeadline = 0
            self.forecastAge = 0
            return False

        history = np.array([history])
        self.forecast = self.forecaster.get(history).numpy().tolist()
        self.forecastAge = timestamp
        self.forecastDeadline = self.forecastAge + self.timeToForecast
        
        # calculating current draw
        self.forecastWithDraw = list(self.forecast)
        step = self.forecaster.forecastLen / len(self.forecast)

        for job in filter(lambda job : job.running, self.jobs):
            duration = m.ceil(job.duration / step)
            started = m.floor((job.started / step) - (self.forecastAge / step))

            for i in range(started, started + duration):
                if i < 0:
                    continue
                if i >= len(self.forecastWithDraw):
                    break    
                self.forecastWithDraw[i] -= job.draw
        return True

    def run(self, timeStamp: int|float, currentProduction: int|float) -> List[Job]:
        result = []
        
        # check forecast
        if self.forecastDeadline <= timeStamp:
            if not self.updateForecast(timeStamp):
                return self.naive.run(timeStamp,currentProduction)
        
        remaningProduction = currentProduction - sum(job.draw for job in self.jobs if job.running)
        self.jobs.sort(key= lambda job : job.deadline if job.deadline != 0 else float("inf"))

        for job in self.jobs:
            if job.deadline and not (job. running or job.finished) and job.deadline - job.duration <= timeStamp + (self.forecaster.timeLen / self.stepsInADay):
                job.deviceCommand(timeStamp)
                result.append(job)
                remaningProduction -= job.draw
                
            if job.running and timeStamp >= job.started + job.duration:
                job.stop()

        for job in self.jobs:
            # fit in schedule if not given an estimat and earliest start within forecast
            if not (job.running or job.finished) and self.jobsSch.get(job.name) != self.forecastDeadline:
                self.fitJob(job,timeStamp)
            
            # start if estimated to run
            if job.started and job.started <= timeStamp and not (job.running or job.finished):
                if job.draw - remaningProduction > self.diff_threshold or remaningProduction < self.start_threshold:
                    continue
                job.deviceCommand(timeStamp) 
                result.append(job)
                remaningProduction -= job.draw
        
        return result

    def fitJob(self,job: Job,timeStamp) -> int:
        """ Finds a spot for the job in the forecast and sets job.started to that time"""
        # converting to steps in the forecast
        forecastEnd = self.forecastAge + self.forecaster.timeLen
        step = (forecastEnd - self.forecastAge) / len(self.forecast)
        diff = forecastEnd - timeStamp 
        location = m.ceil(self.forecaster.forecastLen - diff / step)
        duration = m.ceil(job.duration / step)

        deadline = 0
        if job.deadline and job.deadline < forecastEnd:
            deadline = m.floor((job.deadline - self.forecastAge) / step)


        earliestStart = 0
        if job.earliestStart and job.earliestStart > self.forecastAge:
            # cannot be scheduled within this forecast
            earliestStart = m.ceil((job.earliestStart - self.forecastAge) / step)
            print(earliestStart)
            if earliestStart >= self.forecaster.forecastLen - duration:
                # job cannot run within forecast
                self.jobsSch[job.name] = self.forecastDeadline
                return
            
        bestPlace = location
        bestPrice = float("inf")
        for i in range(location, self.forecaster.forecastLen - duration):
            if earliestStart and earliestStart > i:
                continue

            if deadline and deadline - duration <= i:
                break
            
            price = sum(relu(job.draw - self.forecastWithDraw[j]) for j in range(i, i + duration))
            if  price < bestPrice:
                bestPlace = i
                bestPrice = price
                # early stopping
                if price == 0:
                    break

        # converting to posix
        job.started = self.forecastAge + bestPlace * step

        for i in range(bestPlace, bestPlace + duration):
            if i >= len(self.forecastWithDraw):
                break
            self.forecastWithDraw[i] -= job.draw
    
        self.jobsSch[job.name] = self.forecastDeadline

def relu(number):
    if number > 0:
        return number
    else:
        return 0