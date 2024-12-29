from fastapi import FastAPI, Request, HTTPException
import httpx

app = FastAPI()

# Define backend service URLs
SERVICE1_URL = "http://service1:8000"
SERVICE2_URL = "http://service2:8001"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def reverse_proxy(request: Request, path: str):
    """
    Reverse proxy to route requests to the appropriate service.
    """
    # Determine the target service based on the path
    if path.startswith("service1"):
        target_url = f"{SERVICE1_URL}/{path[len('service1/'):]}"
    elif path.startswith("service2"):
        target_url = f"{SERVICE2_URL}/{path[len('service2/'):]}"
    else:
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
