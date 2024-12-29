from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import logging 

app = FastAPI()

logger = logging.getLogger("service1")  # Use the same logger as Uvicorn
logger.setLevel(logging.INFO)


@app.get("/")
def get_web_page():
    
    html_content = """
    <html>
        <head>
            <title>Service 1</title>
        </head>
        <body>
            <h1>Welcome to Service 1</h1>
            <p>This is a web page returned by Service 1.</p>
        </body>
    </html>
    """
    
    logger.info(f"YOYO")
    
    return HTMLResponse(content=html_content, status_code=200)