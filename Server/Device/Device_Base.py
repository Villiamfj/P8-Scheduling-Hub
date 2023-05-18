from Device.Misc import API_Types, Device_Types

class Device():

    name = ""
    id = 0
    type = "NONE"
    API_Type = "NONE"

    def __init__(self, name: str, id: str, type: str, API_type: str):
        self.name = name
        self.id = id
        self.type = type
        self.API_type = API_type
