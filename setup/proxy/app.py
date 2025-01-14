from fastapi import FastAPI, Request, HTTPException
import httpx
import asyncio
import logging

import pickle

import pandas as pd

from datetime import datetime, timedelta

app = FastAPI()

# Define backend service URLs
SERVICE1_URL = "http://service1:8000"
SERVICE2_URL = "http://service2:8001"

# Configure logger
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

requests = []
timestamps = []

class CustomRequest:
    
    def __init__(self, timestamp, loggedin, error=None):
        self.timestamp = timestamp
        self.loggedin = loggedin
        self.isError = error

    # Getter for timestamp
    def get_timestamp(self):
        return self.timestamp

    # Setter for timestamp
    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    # Getter for loggedin
    def get_loggedin(self):
        return self.loggedin

    # Setter for loggedin
    def set_loggedin(self, loggedin):
        self.loggedin = loggedin

    # Getter for isError
    def get_is_error(self):
        return self.isError

    # Setter for isError
    def set_is_error(self, is_error):
        self.isError = is_error

    # String representation of the object
    def __str__(self):
        return f"CustomRequest(timestamp={self.timestamp}, loggedin={self.loggedin}, isError={self.isError})"
    
        
def count_requests_within_one_second(requests, target_timestamp):
    """
    Counts the number of requests within 1 second of a target timestamp and 
    also counts the requests with isError=True within that time window.

    Args:
        requests (list): A list of Request objects.
        target_timestamp (datetime): The target datetime object.

    Returns:
        tuple: (Total count of requests within 1 second, Count of requests with isError=True within 1 second)
    """
    # Define the time window
    lower_bound = target_timestamp - timedelta(seconds=5)
    #upper_bound = target_timestamp + timedelta(seconds=1)

    # Count requests within the range
    total_count = sum(lower_bound <= req.get_timestamp() for req in requests)

    # Count requests with isError=True within the range
    error_count = sum(lower_bound <= req.get_timestamp() and req.get_is_error() for req in requests)

    return total_count, error_count


def predict(requests, current_request):
    
    
        
    count, error_count = count_requests_within_one_second(requests, current_request.get_timestamp())
    serrorrate = error_count / count
    feature_names = ["loggedin", "count", "serrorrate"]  # Replace with your actual feature names
    loggedin = current_request.get_loggedin()
    
        
    input_features = pd.DataFrame([[loggedin, count, serrorrate]], columns=feature_names)
    
    with open("logistic_regression_model.pkl", "rb") as f:
        loaded_model = pickle.load(f)
        
    return loaded_model.predict(input_features)[0]

def check_login(request: Request):
    """
    Check if the credentials sent in the header match 'admin' and 'admin'.

    Args:
        request (Request): The incoming request object.

    Returns:
        bool: True if credentials match, False otherwise.
    """
    user = request.headers.get("user")
    password = request.headers.get("password")

    return user == "admin" and password == "admin"
    


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def reverse_proxy(request: Request, path: str):
    """
    Reverse proxy to route requests to the appropriate service.
    """
    #metrics.increment_connections()
    logged_in = 1 if check_login(request) else 0
    current_timestamp = datetime.now()
    error = None
    # Determine the target service based on the path
    if path.startswith("service1"):
        target_url = f"{SERVICE1_URL}/{path[len('service1/'):]}"
        if logged_in == 0:
            error = True
        else:
            error = False
    elif path.startswith("service2"):
        target_url = f"{SERVICE2_URL}/{path[len('service2/'):]}"
        if logged_in == 0:
            error = True
        else:
            error = False
    else:
        #metrics.increment_serrorrate()  # Increment serrorrate on invalid paths
        target_url = None
        error = True
        logger.error("Invalid service path encountered")

        #raise HTTPException(status_code=404, detail="Invalid service path")
    
    customrequest = CustomRequest(current_timestamp, logged_in, error)    
    
    requests.append(customrequest)
    result = predict(requests, customrequest)

    logger.info(f"Predict {result}")
    
    if error == False:
    # Forward the request to the appropriate service
        async with httpx.AsyncClient() as client:
            # Forward headers, query params, and body
            headers = dict(request.headers)
            headers.pop("host", None)  # Remove the host header to avoid conflicts
            query_params = dict(request.query_params)
            body = await request.body()

            # Send the request to the target service
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=query_params,
                content=body,
            )
        # Return the response from the target service
        return {
            "content": response.text,
        }
    else:
        return {
            "content": "error",
        }
        

    


"""async def log_background_task():

    while True:
        #current_serrorrate = metrics.get_serrorrate()  # Access serrorrate from the Metrics instance
        #logger.info(f"serrorrate: {current_serrorrate}")
        predict = metrics.predict()
        logger.info(f"model predict: {predict}")
        await asyncio.sleep(10)"""


@app.on_event("startup")
async def start_background_task():
    """
    Start the background logging task when the app starts.
    """
    #asyncio.create_task(log_background_task())

"""curl -X GET "http://127.0.0.1:8080/service1" \
     -H "user: admin" \
     -H "password: admin"""