from Device.Device_Base import Device
from Device.Misc import API_Types, Device_Types
from Schedule.Job import Job
import requests
from Device.Misc import check_HomeConnect_status
from Exceptions import JobFailedException


class Device_HomeConnect(Device):

    def __init__(self, name: str, id: str, type: Device_Types, API_type: API_Types, token:str):
        super(Device_HomeConnect, self).__init__(name, id, type, API_type)
        self.token = token

    
    #home connect shows these as available
    #name = ""             # Name of appliance for Home Connect
    brand = ""              # Brand of appliance
    vib = ""                # Unknown / possibly ID of the specific type of appliance
    connected = False       # Status showing if it is connected (should probably only be "true")
    #type = ""               # General type of appliance
    enumber = ""            # Unknown / similar to vib


    remoteControlState = False  # "true" if remote control is activated
    remoteStartState = False    # "true" if remote start is activated

    #should probably just delete this as it is not useful to remember (but should still be locally checked)
    localControlState = False   # "true" if the home appliance is currently operated locally 

    #This should be checked before deoing anything, Can remember this to have a status available to the user
    #for describtion check: https://api-docs.home-connect.com/states?#operation-state
    operationState = ""         # could be: "Inactive",  "Ready", "Delayed Start", "Run", "Pause", "Action Required", "Finished", "Error", "Aborting"
    
    def CreateJob(self,duration,draw,deadline, earliestStart, arguments):
        return HC_Job(self,duration,draw,deadline,earliestStart,[],arguments)
    
class HC_Job(Job):
    def __init__(self, device: Device_HomeConnect, duration: int | float, draw: int | float, deadline: int | float, earliestStart: int | float, daysToRun: list, arguments):
        super().__init__(device, duration, draw, deadline, earliestStart, daysToRun, device.name, self.RunHomeConnectJob)
        self.device = device
        self.arguments = arguments
    
    def RunHomeConnectJob(self, time):
        # check status
        status = check_HomeConnect_status(self.device.id, self.device.token)
        if status != 1:
            print("already running")
            return

        url_operation = f"https://simulator.home-connect.com/api/homeappliances/{self.device.id}/programs/active"

        headers = {
            "Authorization": f"Bearer {self.device.token}",
            "Content-Type": "application/vnd.bsh.sdk.v1+json"
        }

        data_raw = self.arguments
        response = requests.put(url_operation, headers=headers, data=data_raw)
        if response.status_code == 204:
            self.running = True
            self.started = time        
        else:
            raise JobFailedException(self.device.name, data_raw)

    def stop(self):
        status = check_HomeConnect_status(self.device.id, self.device.token)
        if status == 2:
            self.duration += 120 # 2 minutes
            return
        
        self.running = False
        self.finished = True