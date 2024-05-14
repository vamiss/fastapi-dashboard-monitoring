from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
import psutil
from dash_application import dash_app
from monitor import CPU_COUNT
from security import authorize
from typing import Annotated

app = FastAPI()

app.mount("/dashboard", WSGIMiddleware(dash_app.server))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/cpu/")
async def cpu(user: Annotated[str, Depends(authorize)], cpu_id: int | None = None):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if cpu_id is None:
        return {"cpu": psutil.cpu_percent()}
    else:
        if 0 <= cpu_id < CPU_COUNT:
            return {f"cpu{cpu_id+1}": psutil.cpu_percent(percpu=True)[cpu_id]}
        raise HTTPException(
            status_code=404,
            detail=f"CPU not found. cpu_id must be between 1 and {CPU_COUNT-1}, but got {cpu_id}")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
