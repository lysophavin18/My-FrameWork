"""Resource guard checks CPU/RAM and queue pressure before running scans."""

import psutil
from app.config import settings


def is_system_ready() -> tuple[bool, dict]:
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    ready = cpu < settings.scan_cpu_threshold and ram < settings.scan_ram_threshold
    return ready, {"cpu_percent": cpu, "ram_percent": ram, "ready": ready}
