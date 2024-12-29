from fastapi import FastAPI, Request, HTTPException
import httpx
import asyncio
import logging

import pickle

import pandas as pd



app = FastAPI()

# Define backend service URLs
SERVICE1_URL = "http://service1:8000"
SERVICE2_URL = "http://service2:8001"

# Configure logger
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)


class Metrics:
    """
    A class to encapsulate metrics.
    """
    def __init__(self):
        self.error = 0
        self.connections = 0
        
        with open("logistic_regression_model.pkl", "rb") as f:
            self.loaded_model = pickle.load(f)

    def increment_serrorrate(self):
        """
        Increment the serrorrate by 1.
        """
        self.error += 1
        
    def increment_connections(self):
        """
        Increment the connections by 1.
        """
        self.connections += 1    

    def get_serrorrate(self):
        """
        Get the current value of serrorrate.
        """
        if self.connections != 0:
            rate = self.error / self.connections 
            
        else:
            rate = 10000
        return float(rate)
    
    def get_connections(self):
        """
        Get the current value of connections.
        """
        return self.connections
    
    def predict(self):
        
        logger.info(f"connections: {self.connections}")
        logger.info(f"serrorrate: {self.get_serrorrate()}")
        
        feature_names = ["count", "serrorrate"]  # Replace with your actual feature names
        
        input_features = pd.DataFrame([[self.connections, self.get_serrorrate()]], columns=feature_names)
        
        self.connections = 0
        self.error = 0
        
        return self.loaded_model.predict(input_features)[0]


# Create a global metrics instance
metrics = Metrics()


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def reverse_proxy(request: Request, path: str):
    """
    Reverse proxy to route requests to the appropriate service.
    """
    metrics.increment_connections()
    # Determine the target service based on the path
    if path.startswith("service1"):
        target_url = f"{SERVICE1_URL}/{path[len('service1/'):]}"
    elif path.startswith("service2"):
        target_url = f"{SERVICE2_URL}/{path[len('service2/'):]}"
    else:
        metrics.increment_serrorrate()  # Increment serrorrate on invalid paths
        raise HTTPException(status_code=404, detail="Invalid service path")

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


async def log_background_task():
    """
    Background task that logs the current value of serrorrate every second.
    """
    while True:
        #current_serrorrate = metrics.get_serrorrate()  # Access serrorrate from the Metrics instance
        #logger.info(f"serrorrate: {current_serrorrate}")
        predict = metrics.predict()
        logger.info(f"model predict: {predict}")
        await asyncio.sleep(10)


@app.on_event("startup")
async def start_background_task():
    """
    Start the background logging task when the app starts.
    """
    asyncio.create_task(log_background_task())
