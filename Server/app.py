from flask import Flask, request, redirect, url_for, render_template, jsonify
from Schedule.NaiveScheduler import naiveScheduler, testJob
from Schedule.ForecastScheduler import ForecastScheduler
from Production.Prod_device import Solar_power_device_demo, Solar_power_API
from Manager import loop, set_interval
import requests
from Tools import HomeConnectTools, jsonSerialize, timeParamAsTimestamp, calculateCombinedDraw
from Device import DeviceManager
from Device.Misc import check_HomeConnect_status
from datetime import datetime
from Exceptions import *

deviceManager = DeviceManager.manager()
deviceManager.access_token_HomeConnect = HomeConnectTools.GetToken()
jobs = []

# real
#delayBetweenRuns = 300 # every five minutes
#pingsWithinADay = 86400 / delayBetweenRuns # 86400 seconds in a day
#production = Solar_power_API(pingsWithinADay)

# Demo
delayBetweenRuns = 1
pingsWithinADay = 288 # the set contains 288 points in a day
production = Solar_power_device_demo()
production.counter = 288 # starting at a later stage

sch = ForecastScheduler(
    jobs=jobs,
    start_threshold=0.1, # kW
    diff_threshold=0.1, # kW
    prod_device=production,
    timeBetweenForecast=delayBetweenRuns * 2,
    stepsInADay=pingsWithinADay,
    modelLocation="./Forecast/lstm",
    forecastTimeLen=delayBetweenRuns * pingsWithinADay
)

app = Flask(__name__)

# A page showing the status of the system, with a graph of both production and forecasting
# this endpoint is dependant on the "/stats endpoint."
@app.route("/", methods = ["GET"])
def statusPage():
    return render_template("status.html")

@app.route("/auth_homeconnect", methods=["GET"])
def Auth():
    HomeConnect_clientID = HomeConnectTools.HomeConnect_ReadClientID()
    redirect_uri = "http://" + request.host + "/auth_homeconnect_redirect"
    scope = "IdentifyAppliance Control Settings Monitor"
    response_type = "code"
    
    authorization_url = f"https://simulator.home-connect.com/security/oauth/authorize?response_type={response_type}&client_id={HomeConnect_clientID}&scope={scope}&redirect_uri={redirect_uri}"
    return redirect(authorization_url)

@app.route("/auth_homeconnect_redirect", methods=['GET'])
def Auth_Redirect():
    authorization_code = request.args.get('code','') #NOTE: the blank '' is the default value
    redirect_uri = "http://" + request.host + "/auth_homeconnect_redirect"
    HomeConnect_clientID = HomeConnectTools.HomeConnect_ReadClientID()
    HomeConnect_clientSecret = HomeConnectTools.HomeConnect_ReadClientSecret()
    url_token = 'https://simulator.home-connect.com/security/oauth/token'
    data = {
        'client_id': HomeConnect_clientID,
        'client_secret': HomeConnect_clientSecret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'code': authorization_code
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(url_token, data=data, headers=headers)
    if response.status_code == 200:
        responseData = response.json()
        deviceManager.access_token_HomeConnect = responseData["access_token"]
        deviceManager.refresh_token_HomeConnect = responseData["refresh_token"]
        deviceManager.id_token_HomeConnect = responseData["id_token"]
        HomeConnectTools.SaveToken(responseData["access_token"])
        return redirect(url_for('statusPage'))
    
    else:
        print("Error: ")
        print(response.text)
        return "Something went wrong, could not authenticate the user", response.status_code

@app.route("/Devices/FindDevices", methods=["GET"])
def FindDevices():
    try:
        deviceManager.FindAll()
        return jsonSerialize(deviceManager.allDevices)
    except AccessTokenRefreshFailedException as e:
        print(e)
        return "Could not refresh token, try to authenticate again", 400
    except RequestFailedException as e:
        print(e)
        return "a request failed, the given url might be wrong", 500
    except Exception as e:
        print(e)
        return "Something went wrong, could not find devices",500

@app.route("/ListPrograms", methods=["GET"])
def HomeConnect_List_Programs():
    id = request.args.get('id')
    if not id:
        return "Missing parameters",400
    
    device = deviceManager.allDevices.get(id)
    if not device:
        return "Device not found",400
    
    try:
        response = deviceManager.findDevicePrograms(id)
        return response
    except AccessTokenRefreshFailedException as e:
        print(e)
        return "Could not refresh token, try to authenticate again", 400
    except RequestFailedException as e:
        print(e)
        return "A request failed, the given url might be wrong", 500
    except Exception as e:
        print(e)
        return "Something went wrong, could not find programs",500


@app.route("/ListProgramOptions", methods=["GET"])
def HomeConnect_List_ProgramOptions():
    id = request.args.get('id')
    program = request.args.get('program')
    if not id or not program:
        return "Missing parameters",400
    
    device = deviceManager.allDevices.get(id)
    if not device:
        return "Device not found",400
    
    try:
        response = deviceManager.findDeviceProgramOptions(id, program)
        return response
    except AccessTokenRefreshFailedException as e:
        print(e)
        return "Could not refresh token, try to authenticate again", 400
    except RequestFailedException as e:
        print(e)
        return "a request failed, the given url might be wrong or the given program might not exist", 500
    except Exception as e:
        print(e)
        return "Something went wrong, could not find options", 500
    
@app.route("/schedule", methods = ["POST"])
def add_to_schedule():
    id = request.args.get("id")
    arguments_data = request.args.get("data")
    duration = request.args.get("duration")
    draw = request.args.get("draw")
    if not id or not arguments_data or not duration or not draw:
        return "Missing parameters", 400

    try:
        duration = float(duration)
        draw = float(draw)
    except:
        return "duration or draw is not a float", 400
    
    deadline = 0
    start = 0
    try:
        start = timeParamAsTimestamp(request,"start")
        deadline = timeParamAsTimestamp(request,"deadline")
    except:
        return "Could not interprete the time", 400

    if deadline and start > deadline - duration:
        return "The job can't finish in time", 400

    device = deviceManager.allDevices.get(id)
    if not device:
        return "Device not found", 400
    
    if any(map(lambda job : job.device == device and job.finished == False, jobs)):
        return "Device already scheduled for another job", 200
    
    job = None
    try:
        job = device.CreateJob(duration,draw,deadline,start,arguments_data)
        jobs.append(job)
        return jsonSerialize(job)
    except Exception as e:
        print(e)
        return "Something went wrong, could not Schedule job", 500

@app.route("/scheduleTest", methods = ["POST"])
def add_to_scheduleTest():
    id = request.args.get("id")
    duration = request.args.get("duration")
    draw = request.args.get("draw")
    if not duration or not draw:
        return "Missing parameters", 400

    try:
        duration = float(duration)
        draw = float(draw)
    except:
        return "duration or draw is not a float", 400
    
    deadline = 0
    start = 0
    try:
        start = timeParamAsTimestamp(request,"start")
        deadline = timeParamAsTimestamp(request,"deadline")
    except:
        return "Could not interprete start of deadline", 400
    
    if deadline and start > deadline - duration:
        return "The job can't finish in time", 400

    job = testJob(duration,draw, deadline, start, id)

    jobs.append(job)
    return jsonSerialize(job)

@app.route("/jobStatus", methods = ["GET"])
def get_status():
    try:
        return jsonSerialize(jobs)
    except Exception as e:
        print(e)
        return "Something went wrong", 500

@app.route("/homeConnectStatus", methods = ["GET"])
def status():
    try:
        return jsonSerialize([check_HomeConnect_status(dev.id, deviceManager.access_token_HomeConnect) for dev in deviceManager.allDevices.values()])
    
    except AccessTokenRefreshFailedException as e:
        print(e)
        return "Could not refresh token, try to authenticate again", 400

    except RequestFailedException as e:
        print(e)
        return "a request failed, the given url might be wrong", 500
    
    except Exception as e:
        print(e)
        return "Something went wrong", 500


# An endpoint that gives statistics to give an overview of the state
@app.route("/stats", methods = ["GET"])
def stats():
    now = datetime.now().timestamp()
    tick = delayBetweenRuns

    prody = [i for i in production.get_history()] # makes a copy of the set
    prody.reverse()
    prodx = []
    for index,_ in enumerate(prody):
        prodx.append(now - index * tick)

    forecastx = []
    forecasty = []
    if len(prodx) == pingsWithinADay:
        forecasty = sch.forecast
        forecastTick = delayBetweenRuns * (len(prodx) / len(forecasty))
        forecastx = [sch.forecastAge + i * forecastTick for i in range(len(forecasty))]
    xdraw = prodx + forecastx
    xdraw.sort()
    ydraw = calculateCombinedDraw(sch.jobs,xdraw)

    return jsonify({"xdraw":xdraw, 
                    "ydraw":ydraw, 
                    "prod":prody, 
                    "prodx": prodx,
                    "forecasty": forecasty,
                    "forecastx": forecastx})

if __name__ == '__main__':
    loop(sch,production) # first run
    handle = set_interval(loop, delayBetweenRuns, args=(sch,production))
    app.run(port=8080)