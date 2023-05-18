class RequestFailedException(Exception):
    """Raised when a request fails"""
    def __init__(self, URL: str, response) -> None:
        super().__init__("Request failed for URL: " + URL + " With response: " + response.text)

class AccessTokenRefreshFailedException(Exception):
    """Raised when refreshing the access token fails"""
    def __init__(self, API: str, status: str) -> None:
        super().__init__("Refresh failed for: " + API + " With status: " + status)

class JobFailedException(Exception):
    """Raised when a job fails to start"""
    def __init__(self, deviceName, arguments) -> None:
        super().__init__("Job failed on device: " + deviceName + " with the arguments: " + arguments)
