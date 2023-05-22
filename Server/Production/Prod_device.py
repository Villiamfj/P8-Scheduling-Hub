import pandas as pd
from typing import List
from abc import abstractclassmethod
import requests as req
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# A production device simply has the ability to get_power
class Prod_device:
    @abstractclassmethod
    def get_power(self) -> int:
        pass

    @abstractclassmethod
    def get_history(self) -> List[int]:
        pass

def readUsername() -> str:
    file = open("Secrets(Dont Push)/username")
    return file.read()

def readPassword() -> str:
    file = open("Secrets(Dont Push)/password")
    return file.read()

class Solar_power_API(Prod_device):
    def __init__(self, pinqWithinDay):
        self.history = []
        self.histLen = pinqWithinDay
        self.restartCount = 0
        self.startBrowser()

    def get_power(self) -> int:
        try:
            item = self.browser.find_element(By.ID, 'pvText').text.split(' ')
            power = float(item[0])
            metric = item[1]

            if metric == "W":
                power *= 0.001 #kw
            elif metric != "kW":
                print("unknown metric: ", metric)

            self.history.append(power)
            if len(self.history) > self.histLen:
                self.history.pop(0)
            return power
        except Exception as e:
            if self.restartCount > 2:
                raise Exception("restartCount too big")
            self.restartCount += 1
            print("error met",e)
            print("restarting scraper")
            self.browser.close()
            self.startBrowser()
            sleep(5)
            return self.get_power()
    
    def get_history(self) -> float | int:
        return self.history
    
    def startBrowser(self):
        # Login information
        username = readUsername()
        password = readPassword()

        # Login and navigate to info page
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox") # linux only
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("detach", True)
        browser = webdriver.Chrome(options=chrome_options)

        # Solar web redirect to Fronius login
        browser.get('https://www.solarweb.com/Account/ExternalLogin')

        # Fronius login (login.fronius.com/...)
        username_elem = browser.find_element(By.ID, 'username')  # Find the search box
        username_elem.clear()
        username_elem.send_keys(username)

        password_elem = browser.find_element(By.ID, 'password')  # Find the search box
        password_elem.clear()
        password_elem.send_keys(password)
    
        # Sleep since button needs to load, click login button
        sleep(2)
        browser.find_element(By.ID, 'submitButton').click()

        # cookie skip
        sleep(5)
        browser.find_element(By.XPATH, '//*[@id="CybotCookiebotDialogBodyButtonDecline"]').click()

        # Sleep since table needs to be load, click solar installation on table
        sleep(5)
        #browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td[2]').click()
        browser.find_element(By.XPATH, '//*[@id="1dd84dd8-039e-4e70-92df-819eb3924fe3"]').click()

        self.browser = browser

class Solar_power_device_demo(Prod_device):
    def __init__(self) -> None:
        super().__init__()
        firstDay = [0.307,0.34600000000000003,0.38,0.321,0.372,0.387,0.367,0.379,0.34600000000000003,0.319,0.28500000000000003,0.261,0.229,0.209,0.195,0.185,0.177,0.166,0.147,0.12,0.105,0.089,0.076,0.069,0.059000000000000004,0.048,0.035,0.026000000000000002,0.01,0.006,0.005,0.003,0.003,0.002,0.001,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.001,0.002,0.002,0.002,0.002,0.002,0.002,0.001,0.001,0.001,0.001,0.002,0.002,0.002,0.002,0.002,0.002,0.001,0.001,0.001,0.002,0.002,0.002,0.002,0.002,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.003,0.002,0.004,0.004,0.004,0.004,0.004,0.005,0.005,0.005,0.006,0.006,0.011,0.01,0.013000000000000001,0.015,0.016,0.018000000000000002,0.023,0.029,0.034,0.035,0.041,0.054,0.08,0.057,0.062,0.058,0.054,0.054,0.094,0.089,0.121,0.163,0.23800000000000002,0.362,0.367,0.39,0.397,0.41000000000000003,0.448,0.519,0.558,0.596,0.639,0.555,0.491,0.617,0.742,0.742,0.619,0.511,0.46900000000000003,0.555,0.995,1.05,0.998,0.933,0.631,0.405,0.322,0.23500000000000001,0.20700000000000002,0.185,0.197,0.228,0.20400000000000001,0.186,0.199,0.254,0.278,0.278,0.199,0.195,0.219,0.396,0.8140000000000001,0.863,0.9470000000000001,0.8140000000000001,0.767,0.615,0.615,0.649,0.682,0.769,0.735,0.6970000000000001,0.719,3.2,3.31,3.35,2.74,0.732,2.49,2.66,3.75,1.22,4.16,0.993,0.9540000000000001,1.04,3.95,0.966,3.88,4.08,1.76,3.71,3.73,3.66,3.67,3.65,3.62,3.67,3.67,3.7,3.66,3.64,3.62,3.61,3.63,3.64,3.57,3.47,3.53,3.48,3.47,3.46,3.19,3.4,3.42,3.43,3.33,3.18,3.0,3.38,3.3,3.24,3.26,3.18,3.17,3.09,3.2,3.13,2.5,1.76,2.49,2.22,2.67,1.91,2.06,1.36,1.38,1.41,1.91,1.51,1.78,1.56,2.07,1.39,1.37,1.12,1.15,0.522,1.17,1.56,1.31,1.37,0.9580000000000001,0.674,0.5660000000000001,0.6990000000000001,0.615,0.748,0.47900000000000004,0.435,0.425,0.428,0.365]
        secondDay = [0.455,0.297,0.256,0.269,0.27,0.268,0.28200000000000003,0.219,0.20700000000000002,0.2,0.182,0.183,0.17500000000000002,0.17,0.196,0.199,0.23600000000000002,0.209,0.194,0.222,0.199,0.16,0.14400000000000002,0.139,0.12,0.11800000000000001,0.074,0.065,0.048,0.038,0.026000000000000002,0.016,0.006,0.005,0.003,0.001,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.002,0.003,0.002,0.002,0.003,0.002,0.002,0.002,0.003,0.003,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.001,0.001,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.003,0.002,0.002,0.003,0.002,0.002,0.002,0.002,0.002,0.002,0.002,0.001,0.002,0.002,0.002,0.003,0.003,0.003,0.004,0.004,0.004,0.004,0.004,0.005,0.005,0.005,0.005,0.005,0.005,0.006,0.004,0.004,0.006,0.006,0.009000000000000001,0.012,0.018000000000000002,0.023,0.024,0.03,0.038,0.049,0.068,0.093,0.115,0.153,0.202,0.244,0.252,0.23,0.193,0.202,0.184,0.184,0.163,0.165,0.185,0.201,0.22,0.255,0.23,0.186,0.23500000000000001,0.302,0.216,0.26,0.357,0.316,0.422,0.463,0.422,0.353,0.34900000000000003,0.39,0.502,0.6990000000000001,0.796,0.757,0.795,0.6920000000000001,0.663,0.63,0.505,0.6890000000000001,0.612,0.6960000000000001,0.877,1.14,1.29,1.31,1.11,1.18,1.12,1.0,0.855,1.3,1.12,1.54,1.28,1.01,1.03,1.29,1.8,1.51,2.58,2.9,2.13,2.27,1.67,1.79,1.77,1.46,1.55,1.38,1.19,1.08,1.21,1.84,1.66,2.32,1.7,1.56,1.7,1.31,1.65,1.86,2.03,1.86,2.52,2.51,1.88,2.63,1.71,1.92,2.03,1.71,1.85,2.38,1.69,1.56,1.89,1.84,2.17,1.98,2.07,1.91,2.37,1.79,2.18,2.33,1.65,1.95,1.72,1.97,1.71,1.81,2.01,2.01,3.24,1.82,1.87,1.7,1.88,1.74,1.56,1.53,1.73,1.86,2.06,1.91,1.58,1.91,1.54,2.31,1.73,1.79,2.13,1.53,1.64,1.91,2.03,1.77,1.69,1.33,1.75,1.52,1.31,1.52,0.85,0.805,0.748,0.72,0.7020000000000001,0.678,0.605,0.587,0.613,0.629,0.511,0.499,0.47300000000000003,0.401,0.357,0.318]
        firstDay.reverse()
        secondDay.reverse()
        self.data = firstDay + secondDay
        self.counter = 0

    def get_power(self) -> int:
        result = self.data[self.counter]
        self.counter +=1
        if self.counter >= len(self.data): self.counter = 0
        return result # kw
    
    def get_history(self) -> List[int]:
        """ returns history data, which can be used to forecast"""
        if self.counter >= 288: # the dataset contains 96 steps per day
            return [i for i in self.data[self.counter - 288: self.counter]]
        return [i for i in self.data[0 : self.counter]]

class Wind_power_device_demo(Prod_device):
    def __init__(self) -> None:
        super().__init__()
        data = pd.read_csv("data_swt_iee_usp_2022.csv", sep=";")
        self.data = data["Power out"]
        self.counter = 0

    def get_power(self) -> float|int:
        result = self.data[self.counter]
        self.counter +=1
        if self.counter >= len(self.data): self.counter = 0
        return result
    
    def get_history(self) -> List[float|int]:
        """ returns history data, which can be used to forecast"""
        return [i for i in self.data[self.counter - 96: self.counter]]