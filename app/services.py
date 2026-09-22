from __future__ import annotations
import os
import json
import uuid
import threading
from datetime import datetime


file_lock = threading.Lock()

class ServerService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with file_lock:
                with open(self.file_path, "w") as file:
                    json.dump([], file)

    def _read_file(self) -> list:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r") as file:
            try:
                servers_list = json.load(file)
                return servers_list if isinstance(servers_list, list) else []
            except json.JSONDecodeError:
                return []

    def _write_file(self, data: list):
        with file_lock:
            with open(self.file_path, "w") as file:
                json.dump(data, file, indent=4)

    def _deep_merge(self, target_dict: dict, source_dict: dict) -> dict:
        for key, value in source_dict.items():
            if key in target_dict and isinstance(target_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(target_dict[key], value)
            else:
                target_dict[key] = value
        return target_dict

    # --- Core CRUD Rules ---

    def get_all_servers(self) -> list:
        return self._read_file()

    def get_server_by_id(self, server_id: str) -> dict | None:
        servers_list = self._read_file()
        return next((srv for srv in servers_list if srv.get("server_id") == server_id), None)

    def create_server(self, server_name: str) -> dict:
        servers_list = self._read_file()
        
        new_server = {
            "server_name": server_name,
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
        
        servers_list.append(new_server)
        self._write_file(servers_list)
        return new_server

    def update_server(self, server_id: str, update_data: dict) -> list | None:
        servers_list = self._read_file()
        
        target_server = next((srv for srv in servers_list if srv.get("server_id") == server_id), None)
        if target_server is None:
            return None
            
        self._deep_merge(target_server, update_data)
        self._write_file(servers_list)
        return list(update_data.keys())

    def delete_server(self, server_id: str) -> bool:
        servers_list = self._read_file()
        initial_length = len(servers_list)
        
        servers_list = [srv for srv in servers_list if srv.get("server_id") != server_id]
        
        if len(servers_list) == initial_length:
            return False
            
        self._write_file(servers_list)
        return True
