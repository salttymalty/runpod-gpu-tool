#!/usr/bin/env python3
import os
import time
import runpod
import subprocess
import sys

API_KEY = os.getenv("RUNPOD_API_KEY")
POD_ID = os.getenv("RUNPOD_POD_ID")
SSH_ALIAS = "runpod"
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_gpu_pod")

if not API_KEY or not POD_ID:
    print("❌ RUNPOD_API_KEY or RUNPOD_POD_ID not set.")
    sys.exit(1)

runpod.api_key = API_KEY

def get_pod_info():
    try:
        return runpod.get_pod(POD_ID)
    except Exception as e:
        print("❌ Failed to fetch pod info:", e)
        sys.exit(1)

def resume_pod():
    print("⏩ Resuming pod...")
    runpod.resume_pod(POD_ID, gpu_count=1)
    for i in range(30):
        pod = get_pod_info()
        status = pod.get("desiredStatus")
        print(f"⌛ Poll {i+1}: {status}")
        if status == "RUNNING":
            print("✅ Pod is running.")
            return pod
        time.sleep(5)
    raise TimeoutError("❌ Pod didn't reach RUNNING status.")

def pause_pod():
    print("🛑 Stopping pod...")
    try:
        runpod.stop_pod(POD_ID)
        print("⏳ Waiting for pod to stop...")
        for i in range(20):
            pod = get_pod_info()
            status = pod.get("desiredStatus")
            print(f"⌛ Poll {i+1}: {status}")
            if status == "STOPPED" or status == "EXITED":
                print("✅ Pod successfully stopped.")
                return
            time.sleep(5)
        raise TimeoutError("❌ Pod did not stop in time.")
    except Exception as e:
        print("❌ Error while stopping pod:", e)
        sys.exit(1)

def extract_ssh_info(pod):
    runtime = pod.get("runtime", {})
    for p in runtime.get("ports", []):
        if p.get("privatePort") == 22 and p.get("isIpPublic", False):
            return p.get("ip"), p.get("publicPort")
    raise Exception("❌ SSH port not found in pod runtime.")

def update_ssh_config(ip, port):
    ssh_config_path = os.path.expanduser("~/.ssh/config")
    host_block = f"""Host {SSH_ALIAS}
    HostName {ip}
    Port {port}
    User root
    IdentityFile {SSH_KEY_PATH}
    StrictHostKeyChecking no
"""

    if os.path.exists(ssh_config_path):
        with open(ssh_config_path, "r") as f:
            config = f.read()
        if SSH_ALIAS in config and ip in config:
            print("🧠 SSH config already up-to-date.")
            return
        print("🔧 Updating SSH config...")

    with open(ssh_config_path, "a") as f:
        f.write("\n" + host_block)

def ssh_into_pod():
    print(f"🔌 Connecting to pod with: ssh {SSH_ALIAS}")
    subprocess.run(["ssh", SSH_ALIAS])

def print_status():
    pod = get_pod_info()
    print("📡 Pod Info:")
    print(f" • Name: {pod.get('name')}")
    print(f" • Status: {pod.get('desiredStatus')}")
    print(f" • Type: {pod.get('podType')}")
    print(f" • GPU: {pod.get('machine', {}).get('gpuDisplayName')}")
    print(f" • Cost/hr: ${pod.get('costPerHr')}")
    print(f" • Volume: {pod.get('volumeInGb')}GB")
    print(f" • Image: {pod.get('imageName')}")

# --- Entry Point ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: runpod_ctl.py [start|pause|ssh|status]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "start":
        pod = resume_pod()
        ip, port = extract_ssh_info(pod)
        update_ssh_config(ip, port)
        ssh_into_pod()

    elif cmd == "pause":
        pause_pod()

    elif cmd == "ssh":
        pod = get_pod_info()
        ip, port = extract_ssh_info(pod)
        update_ssh_config(ip, port)
        ssh_into_pod()

    elif cmd == "status":
        print_status()

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: runpod_ctl.py [start|pause|ssh|status]")
        sys.exit(1)
