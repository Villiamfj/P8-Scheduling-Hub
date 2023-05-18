import json
from Schedule.Job import Job
import requests
from datetime import datetime
from flask import request
from typing import List

def jsonSerialize(obj, indent = 0) -> str:
    """A generic toJson function for python objects"""
    return json.dumps(obj, default=lambda o : o.__dict__, sort_keys=True, indent=indent)

class HomeConnectTools():
    def HomeConnect_ReadClientID() -> str:
        file = open("Secrets(Dont Push)/HomeConnect_ClientID")
        return file.read()


    def HomeConnect_ReadClientSecret() -> str:
        file = open("Secrets(Dont Push)/HomeConnect_ClientSecret")
        return file.read()
    
    def SaveToken(token) -> None:
        file = open("Secrets(Dont Push)/token", "w")
        file.write(token)
    
    def GetToken() -> str:
        """tries to get token, returns \"\" if no tokens found"""
        try:
            file = open("Secrets(Dont Push)/token")
            return file.read()
        except:
            return ""

def convertToTimestamp(timeStr: str, formatStr = '%Y:%m:%d:%H:%M:%S,%f'):
    """converts a string containing the time to a posix timestamp"""
    datetime_object = datetime.strptime(timeStr, formatStr)
    return datetime_object.timestamp()

def timeParamAsTimestamp(request, key:str) -> int:
    """
    Takes a request and the param key and converts it to a timestamp,
    if non are given it will return 0. the expected format is: 
    "year-month-day hour:minute:secound"
    """
    input = request.args.get(key)
    if input == "": return 0

    return convertToTimestamp(input, "%Y-%m-%d %H:%M:%S")

def calculateCombinedDraw(jobs:List[Job], timestampSet:List[float]):
    result = []
    
    for i in timestampSet:
        draw = 0
        for job in jobs:
            if i >= job.started and i <= job.started + job.duration:
                draw += job.draw
        result.append(draw)
    return result
