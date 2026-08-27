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
vps_name = os.getenv("name")


def send_tg(text):
    token = os.getenv("botoken")
    chat_id = os.getenv("chatid")

    if not token or not chat_id:
        print("错误：环境变量 botoken/chatid 未设置")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=5)
    except Exception:
        pass


while True:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    if cpu >= CPU_THRESHOLD:
        send_tg(f"[{vps_name}] CPU 高占用: {cpu:.1f}%")

    if mem >= MEM_THRESHOLD:
        send_tg(f"[{vps_name}] 内存高占用: {mem:.1f}%")

    if disk >= DISK_THRESHOLD:
        usage = psutil.disk_usage("/")
        free_gb = usage.free / 1024**3
        send_tg(f"[{vps_name}] 磁盘空间不足: {disk:.1f}% 剩余 {free_gb:.1f}GB")

    time.sleep(CHECK_INTERVAL)
