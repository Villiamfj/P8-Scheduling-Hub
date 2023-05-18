from enum import Enum
import requests
import json

class API_Types(Enum):
    NONE = 0
    HOMECONNECT = 1

class Device_Types(Enum):
    NONE = 0
    COFFEMACHINE = 1
    OVEN = 2

class HC_Device_Status(Enum):
    NOT_AVAILABLE = 0
    READY = 1
    RUNNING = 2
    FINISHED = 3


def check_HomeConnect_status(haId, access_token) -> int:
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }
    response = requests.get(f'https://simulator.home-connect.com/api/homeappliances/{haId}/status/BSH.Common.Status.OperationState', headers=headers)

    if response.status_code == 200:
        responseData = response.json()["data"]
    else: 
        print(response.text)
        return 0

    not_avalable_list = ["BSH.Common.EnumType.OperationState.Inactive", 
                         "BSH.Common.EnumType.OperationState.ActionRequired",
                         "BSH.Common.EnumType.OperationState.Error"]
    ready_list = ["BSH.Common.EnumType.OperationState.Ready"]
    running_list = ["BSH.Common.EnumType.OperationState.DelayedStart",
                    "BSH.Common.EnumType.OperationState.Run",
                    "BSH.Common.EnumType.OperationState.Pause",
                    "BSH.Common.EnumType.OperationState.Aborting"]
    finished_list = ["BSH.Common.EnumType.OperationState.Finished"]


    if responseData["value"] in not_avalable_list:
        return 0
    if responseData["value"] in ready_list:
        return 1
    if responseData["value"] in running_list:
        return 2
    if responseData["value"] in finished_list:
        return 3

    #should not get here
    return 0

