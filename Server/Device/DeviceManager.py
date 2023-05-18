import requests
import json
from Tools import HomeConnectTools
from Device.Device_HomeConnect import *
from Exceptions import RequestFailedException, AccessTokenRefreshFailedException

class manager():

    allDevices:dict = {}

    access_token_HomeConnect = ""
    refresh_token_HomeConnect = ""
    id_token_HomeConnect = ""

    ### Finding devices 

    def Find_HomeConnect(self):

        url = "https://simulator.home-connect.com/api/homeappliances"

        headers = {
            'Authorization': 'Bearer ' + self.access_token_HomeConnect,
        }

        #This is the simulator link. For real use the non-simulator should be used

        response = self.request_AutoRefreshToken(url, headers)
        
        self.allDevices.clear()

        if response.status_code == 200:
            newDevices = response.json() #should be a dictionary which the "data" item should contain a dictionary of dictionaries of the different devices

            #see https://api-docs.home-connect.com/quickstart?#monitoring for possible response
            for device in newDevices['data']['homeappliances']: #should only contain 1 item so it will also be the first element (hence 0 should work)
                dvice = Device_HomeConnect(device['name'], device["haId"], device['type'], "HOMECONNECT", self.access_token_HomeConnect)
                
                #the rest of the information is not currently needed for anything so it could possibly be deleted. ("connected" might be needed)
                dvice.brand = device['brand']
                dvice.vib = device['vib']
                dvice.connected = device['connected']
                dvice.enumber = device['enumber']

                self.allDevices[device['haId']] = dvice
        else:

            #do nothing. TODO: change to be useful
            pass

    def FindAll(self):
        if self.access_token_HomeConnect: #empty strings are "False"
            self.Find_HomeConnect()
    
    def refreshAccessToken(self): #TODO: make more generic to work with more than HomeConnect
        refresh_endpoint = "https://simulator.home-connect.com/security/oauth/token"
        
        client_id = HomeConnectTools.HomeConnect_ReadClientID()
        client_secret = HomeConnectTools.HomeConnect_ReadClientSecret()
        refresh_token = self.refresh_token_HomeConnect

        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(refresh_endpoint, data=data, headers=headers)
        responseData = response.json()

        if response.status_code == 200:
            HomeConnectTools.SaveToken(responseData["access_token"])
            self.access_token_HomeConnect = responseData["access_token"]
            self.refresh_token_HomeConnect = responseData["refresh_token"]
            self.id_token_HomeConnect = responseData["id_token"]
        else:
            raise AccessTokenRefreshFailedException("HomeConnect", str(response.status_code))
    
    def findDevicePrograms(self, deviceID):
        if self.allDevices[deviceID].API_type == "HOMECONNECT":
            return self.findDevicePrograms_HomeConnect(deviceID)

    def findDeviceProgramOptions(self, deviceID, program):
        if self.allDevices[deviceID].API_type == "HOMECONNECT":
            return self.findDeviceProgramOptions_HomeConnect(deviceID, program)

    def findDeviceProgramOptions_HomeConnect(self, deviceID, program):
        access_token = HomeConnectTools.GetToken()
        url = f'https://simulator.home-connect.com/api/homeappliances/{deviceID}/programs/available/{program}'

        headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/vnd.bsh.sdk.v1+json",
            "Accept-Language": "en-GB"
        }

        response = self.request_AutoRefreshToken(url, headers)
        return response.json()

    def findDevicePrograms_HomeConnect(self, deviceID):
        access_token = HomeConnectTools.GetToken()
        url = f"https://simulator.home-connect.com/api/homeappliances/{deviceID}/programs/available"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/vnd.bsh.sdk.v1+json",
            "Accept-Language": "en-GB"
        }

        response = self.request_AutoRefreshToken(url, headers)
        return response.json()
    
    def request_AutoRefreshToken(self, url: str, header: dict):

        response = requests.get(url, headers=header)

        if response.status_code == 200:
            return response
        elif response.status_code == 401:
            self.refreshAccessToken()
            response = requests.get(url, headers=header)
            if response.status_code == 200:
                return response

        raise RequestFailedException(url, response)




