from pydantic import BaseModel
from typing import Optional

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