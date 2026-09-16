from fastapi import FastAPI,status, HTTPException
import uuid
from pydantic import BaseModel
from datetime import datetime
import os
from typing import Any, Dict, Optional
import json 
app=FastAPI()

class CreateServer(BaseModel):
    server_name: str

class CPUhealthPatch(BaseModel):
    status: Optional[str]=None
    health_utilization_percentage: Optional[float]=None
    core_count: Optional[int]=None
    utilization: Optional[float]=None

class MemoryhealthPatch(BaseModel):
    status: Optional[str]=None
    total_gb: Optional[int]=None
    used_gb: Optional[float]=None
    available_gb : Optional[float]=None

class DiskhealthPatch(BaseModel):
    status: Optional[str]=None
    read_ops_sec: Optional[int]=None
    write_ops_sec: Optional[int]=None
    storage_warning_triggered: Optional[bool]=None

class BatteryhealthPatch(BaseModel):
    status: Optional[str]=None
    type: Optional[str]=None
    charge_percentage: Optional[float]=None
    estimated_runtime_minutes: Optional[int]=None

class NetworkhealthPatch(BaseModel):
    status: Optional[str]=None
    packet_loss_percentage: Optional[float]=None
    latency_ms: Optional[float]=None


class MetricUpdate(BaseModel):
    cpu_health: Optional[CPUhealthPatch] = None
    memory_health: Optional[MemoryhealthPatch] = None
    disk_health: Optional[DiskhealthPatch]=None
    battery_health:Optional[BatteryhealthPatch]=None
    network_health: Optional[NetworkhealthPatch]=None
    panic_check_kernel_panic_detected: Optional[bool]=None
    panic_check_last_panic_timestamp: Optional[bool] = None
    panic_check_error_logs_count: Optional[int]=None
    thermal_level_check_status: Optional[str]=None
    thermal_level_check_current_temperature_celsius: Optional[float]=None
    thermal_level_check_critical_threshold_celsius: Optional[float]=None
    thermal_level_check_fan_speed_rpm: Optional[int]=None
    
@app.get('/health')
def health():
    return {'status':"success"}

@app.get('/api/servers')
async def get_server():
    file_path="servers.json"
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

@app.post("/api/servers", status_code=status.HTTP_201_CREATED)
async def create_server(payload: CreateServer):
    # Create dummy data for the new server
    new_server = {
      "server_name": payload.server_name,
      "server_id": f"srv-{uuid.uuid4()}",
      "timestamp": datetime.utcnow().isoformat() + "Z",
      "status": "healthy",
      "metrics": {
        "cpu_health": {"status": "healthy", "utilization_percentage": 0.0},
        "memory_health": {"status": "healthy", "used_gb": 0.0},
        "disk_health": {"status": "healthy", "storage_warning_triggered": False},
        "battery_health": {"status": "healthy", "charge_percentage": 100.0},
        "network_health": {"status": "healthy", "packet_loss_percentage": 0.0},
        "panic_check": {"kernel_panic_detected": False},
        "thermal_level_check": {"status": "healthy", "current_temperature_celsius": 35.0}
      }
    }
    # Initialize an empty list for servers
    servers_list = []

    #  Read existing data if the file already exists
    if os.path.exists('servers.json'):
        with open('servers.json', "r") as file:
            try:
                servers_list = json.load(file)
                # Ensure the file content is actually a list
                if not isinstance(servers_list, list):
                    servers_list = []
            except json.JSONDecodeError:
                # Handle case where file exists but is corrupted or empty
                servers_list = []

    # Append the fresh server data to the array
    servers_list.append(new_server)

    # Write the updated list back to the JSON file
    with open("servers.json", "w") as file:
        json.dump(servers_list, file, indent=4)

    # Return a custom success response to the client
    return {
        "status": "success",
        "message": f"Server '{payload.server_name}' successfully added to database.",
        "server_id": new_server["server_id"]
    }

@app.patch("/api/servers/{server_id}/payload",status_code=status.HTTP_200_OK)
async def update_server(payload:MetricUpdate):
