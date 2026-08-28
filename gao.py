#!/usr/bin/env python3
import time
import requests
import psutil
import os

# ===== 配置 =====
CHECK_INTERVAL = 60

CPU_THRESHOLD = 1.5     # CPU 超过 1.5 个核心才报警
MEM_THRESHOLD = 98.0
DISK_THRESHOLD = 90.0
# ================

vps_name = os.getenv("name")


def send_tg(text):
    token = os.getenv("botoken")
    chat_id = os.getenv("chatid")

    if not token or not chat_id:
        print("错误：环境变量 botoken/chatid 未设置")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        requests.post(
            url,
            data={
                "chat_id": chat_id,
                "text": text
            },
            timeout=5
        )
    except Exception:
        pass


while True:
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()

    # 换算成实际使用了多少个 CPU 核心
    cpu_cores = cpu_percent * cpu_count / 100

    mem = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/")
    disk = disk_usage.percent

    if cpu_cores >= CPU_THRESHOLD:
        send_tg(
            f"[{vps_name}] CPU 高占用: "
            f"{cpu_percent:.1f}% ({cpu_cores:.2f}/{cpu_count} 核)"
        )

    if mem >= MEM_THRESHOLD:
        send_tg(
            f"[{vps_name}] 内存高占用: {mem:.1f}%"
        )

    if disk >= DISK_THRESHOLD:
        free_gb = disk_usage.free / 1024**3

        send_tg(
            f"[{vps_name}] 磁盘空间不足: "
            f"{disk:.1f}% 剩余 {free_gb:.1f}GB"
        )

    time.sleep(CHECK_INTERVAL)