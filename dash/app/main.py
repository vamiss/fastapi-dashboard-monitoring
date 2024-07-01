from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
import psutil
from dash_application import dash_app
from monitor import CPU_COUNT
from security import authorize, HASHED_USERNAME
from typing import Annotated

app = FastAPI()

app.mount("/dashboard", WSGIMiddleware(dash_app.server))

got_username = HASHED_USERNAME

@app.get("/")
async def root():
    return {"message": "You're in the root FastAPI's directory. It is now ready to work. Type '/dashboard' in your browser's URL to see the dashboard or '/docs' to see the documentation."}

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

@app.get("/info/")
async def get_system_info(user: Annotated[str, Depends(authorize)], parameter: str):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if parameter == "cpu":
        return {
            "cpu_percent": psutil.cpu_percent(),
            "cpu_freq": psutil.cpu_freq()._asdict(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_count_physical": psutil.cpu_count(logical=False)
        }
    elif parameter == "ram":
        return psutil.virtual_memory()._asdict()
    elif parameter == "swap":
        return psutil.swap_memory()._asdict()
    elif parameter == "disk":
        return {part.mountpoint: psutil.disk_usage(part.mountpoint)._asdict() for part in psutil.disk_partitions()}
    elif parameter == "network":
        return psutil.net_io_counters()._asdict()
    elif parameter == "connections":
        connections = psutil.net_connections()
        return [
            {
                "fd": conn.fd,
                "family": str(conn.family),
                "type": str(conn.type),
                "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
                "status": conn.status
            }
            for conn in connections
        ]
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameter. Valid parameters are: cpu, ram, swap, disk, network, connections"
        )

@app.get("/summary/")
async def get_system_summary(user: Annotated[str, Depends(authorize)]):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    cpu_info = {
        "cpu_percent": psutil.cpu_percent(),
        "cpu_freq": psutil.cpu_freq()._asdict(),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False)
    }
    
    ram_info = psutil.virtual_memory()._asdict()
    swap_info = psutil.swap_memory()._asdict()
    
    disk_info = {part.mountpoint: psutil.disk_usage(part.mountpoint)._asdict() for part in psutil.disk_partitions()}
    
    network_info = psutil.net_io_counters()._asdict()
    
    summary = {
        "cpu": cpu_info,
        "ram": ram_info,
        "swap": swap_info,
        "disk": disk_info,
        "network": network_info
    }
    
    return summary

@app.get("/dashboard/")
async def dashboard(user: Annotated[str, Depends(authorize)]):
    return WSGIMiddleware(dash_app.server)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)