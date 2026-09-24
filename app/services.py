from __future__ import annotations
import os
import json
import uuid
import threading
import tempfile
from datetime import datetime


file_lock = threading.Lock()

class ServerService:
    def _ensure_file_exists(self):
        """Safely initializes an empty JSON array if the file doesn't exist."""
        with file_lock:
            if not os.path.exists(self.file_path):
                try:
                    with open(self.file_path, "w", encoding="utf-8") as file:
                        json.dump([], file)
                except (OSError, IOError) as e:
                    raise RuntimeError(f"Failed to initialize database file: {e}")

    def _read_file(self) -> list:
        """Thread-safe read that catches file-system shifts and parsing errors."""
        with file_lock:  # CRITICAL: Lock added to prevent reading half-written data
            if not os.path.exists(self.file_path):
                return []
            try:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    servers_list = json.load(file)
                    return servers_list if isinstance(servers_list, list) else []
            except (json.JSONDecodeError, OSError, IOError):
                # Logger note: Log this error instead of failing silently in production
                return []

    def _write_file(self, data: list):
        """Thread-safe, atomic write using a temp file to prevent data corruption."""
        with file_lock:
            dir_name = os.path.dirname(os.path.abspath(self.file_path))
            
            try:
                # 1. Write to a temporary file in the same directory
                with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as temp_file:
                    json.dump(data, temp_file, indent=4)
                    temp_file_path = temp_file.name

                # 2. Atomically overwrite the destination file
                os.replace(temp_file_path, self.file_path)
                
            except (OSError, IOError) as e:
                # Clean up temp file if something went wrong before os.replace
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                raise RuntimeError(f"Database write failed. Data preserved in-memory: {e}")

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
        clean_name=server_name.strip()
        if not clean_name:
            raise ValueError("Server name cannot be empty and consist soley of spaces")
        servers_list = self._read_file()

        for srv in servers_list:
            if srv.get("server_name", "").lower() == clean_name.lower():
                raise ValueError(f"A server named '{clean_name}' already exists.")
            
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
