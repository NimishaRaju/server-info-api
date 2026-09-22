from fastapi import FastAPI,status, HTTPException
import uuid
from pydantic import BaseModel
from datetime import datetime
import os
from typing import Any, Dict, Optional
import json 
import logging
app=FastAPI()

logger = logging.getLogger("uvicorn.error")
FILE_PATH="servers.json"
class CreateServer(BaseModel):
    server_name: str

class CPUhealthPatch(BaseModel):
    status: Optional[str]=None
    utilization_percentage: Optional[float]=None
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

class PanichealthPatch(BaseModel):
    kernel_panic_detected: Optional[bool]=None
    last_panic_timestamp: Optional[bool] = None
    error_logs_count: Optional[int]=None

class ThermalhealthPatch(BaseModel):
    status: Optional[str]=None
    current_temperature_celsius: Optional[float]=None
    critical_threshold_celsius: Optional[float]=None
    fan_speed_rpm: Optional[int]=None

class MetricUpdate(BaseModel):
    cpu_health: Optional[CPUhealthPatch] = None
    memory_health: Optional[MemoryhealthPatch] = None
    disk_health: Optional[DiskhealthPatch]=None
    battery_health:Optional[BatteryhealthPatch]=None
    network_health: Optional[NetworkhealthPatch]=None
    panic_check: Optional[PanichealthPatch]=None
    thermal_level_check: Optional[ThermalhealthPatch]=None

class ServerMetricPatchRequest(BaseModel):
    server_name: Optional[str] = None
    server_id: Optional[str] = None
    timestamp: Optional[str] = None
    status: Optional[str] = None
    metrics: Optional[MetricUpdate] = None

@app.get('/health')
def health():
    return {'status':"success"}

@app.get('/api/servers')
async def get_server():
    with open(FILE_PATH, "r") as file:
        data = json.load(file)
    return data

@app.get('/api/servers/{server_id}',status_code=status.HTTP_200_OK)
async def get_server(server_id:str):
    with open(FILE_PATH, "r") as file:
        servers_list = json.load(file)
    target_server = None
    for server in servers_list:
        if server.get("server_id") == server_id:
            target_server = server
            break
    return target_server

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
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
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
    with open(FILE_PATH, "w") as file:
        json.dump(servers_list, file, indent=4)

    # Return a custom success response to the client
    return {
        "status": "success",
        "message": f"Server '{payload.server_name}' successfully added to database.",
        "server_id": new_server["server_id"]
    }

def deep_merge(target_dict: dict, source_dict: dict) -> dict:
    for key, value in source_dict.items():
        if key in target_dict and isinstance(target_dict[key], dict) and isinstance(value, dict):
            deep_merge(target_dict[key], value)
        else:
            target_dict[key] = value
    return target_dict

@app.patch("/api/servers/{server_id}",status_code=status.HTTP_200_OK)
def update_server(server_id: str,payload:ServerMetricPatchRequest):
    """
    HTTP PATCH Route. Targets the server by validating the path param
    against the 'server_id' field inside the single-object JSON file.
    """
    if not os.path.exists(FILE_PATH):
        raise HTTPException(status_code=404, detail="file not found.")

   # Read the JSON file (which is a list of servers)
    with open(FILE_PATH, "r") as file:
        servers_list = json.load(file)  # This is a list []


    # Find the specific server dictionary inside the list
    target_server = None
    for server in servers_list:
        if server.get("server_id") == server_id:
            target_server = server
            break

    # If no matching server_id was found in the list, raise a 404
    if target_server is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Server with ID '{server_id}' not found in the file."
        )

    # Extract ONLY the fields the client explicitly sent
    update_data = payload.model_dump(exclude_unset=True)

    # Deep merge the partial updates into the found server object
    deep_merge(target_server, update_data)

    #  Save the entire updated list back to the file
    with open(FILE_PATH, "w") as file:
        json.dump(servers_list, file, indent=4)

    return {
        "message": f"Server '{server_id}' updated successfully", 
        "updated_fields": list(update_data.keys())
    }

@app.delete("/api/servers/delete/{server_id}",status_code=status.HTTP_200_OK)
def delete_server(server_id:str):
    """
    HTTP DELETE Route. Finds the server matching the path parameter
    and removes it from the list inside the JSON file.
    """
    logger.info(f"🚀 ROUTE ACCESSED! Looking for ID: {server_id}")
    if not os.path.exists(FILE_PATH):
        raise HTTPException(status_code=404, detail="Database file not found.")

    #  Read the JSON file list
    with open(FILE_PATH, "r") as file:
        servers_list = json.load(file)

    # Track the initial count of servers
    initial_length = len(servers_list)

    # Filter out the server with the matching ID
    # This keeps every item EXCEPT the one you want to delete
    servers_list = [server for server in servers_list if server.get("server_id") != server_id]

    # If the list length didn't change, the ID doesn't exist
    if len(servers_list) == initial_length:
        raise HTTPException(
            status_code=404, 
            detail=f"Server with ID '{server_id}' not found."
        )

    # Write the shortened list back to the JSON file
    with open(FILE_PATH, "w") as file:
        json.dump(servers_list, file, indent=4)

    return {"message": f"Server '{server_id}' successfully deleted."}