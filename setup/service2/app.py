from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse

app = FastAPI()

@app.get("/file")
def get_file():
    # Ensure the file "example.txt" exists in the service2 directory
    return FileResponse("example.txt")

@app.get("/text")
def get_plain_text():
    return PlainTextResponse("This is plain text returned by Service 2.")