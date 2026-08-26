#!/usr/bin/env python3
import time
import requests
import psutil
import os

# ===== 配置 =====
CHECK_INTERVAL = 60      # 每60秒检查一次
CPU_THRESHOLD = 98.0
MEM_THRESHOLD = 98.0
DISK_THRESHOLD = 90.0    # 磁盘使用率超过90%报警
# ================

def send_bark(title, body):
    url =os.getenv(f"{url}/{title}/{body}")
    try:
        requests.get(url, timeout=5)
    except Exception:
        pass

while True:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    if cpu >= CPU_THRESHOLD:
        send_bark("4GVPS CPU高占用", f"CPU: {cpu:.1f}%")

    if mem >= MEM_THRESHOLD:
        send_bark("4GVPS 内存高占用", f"内存: {mem:.1f}%")

    if disk >= DISK_THRESHOLD:
        usage = psutil.disk_usage("/")
        free_gb = usage.free / 1024**3
        send_bark(
            "4GVPS 磁盘空间不足",
            f"磁盘: {disk:.1f}% 剩余: {free_gb:.1f}GB"
        )

    time.sleep(CHECK_INTERVAL)
