#!/usr/bin/env python3

import json
import os
import paramiko
import sys
from datetime import datetime


def load_config(path="config2.json"):
    with open(path, "r") as f:
        return json.load(f)


def ssh_connect(ip, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=ip,
        username=username,
        password=password,
        timeout=10,
        allow_agent=False,
        look_for_keys=False
    )
    return client


def upload_file(sftp, local_file, remote_folder):
    try:
        sftp.mkdir(remote_folder)
    except IOError:
        pass  # folder already exists

    filename = os.path.basename(local_file)
    remote_path = f"{remote_folder}/{filename}"

    sftp.put(local_file, remote_path)
    return remote_path


def deploy_to_host(ip, username, password, local_file, remote_folder):
    print(f"\n=== [{ip}] Starting upload ===")

    # Track status for reporting
    status = {
        "ip": ip,
        "connected": False,
        "uploaded": False,
        "remote_path": None,
        "error": None
    }

    try:
        client = ssh_connect(ip, username, password)
        status["connected"] = True
        print(f"[{ip}] Connected successfully.")
    except Exception as e:
        status["error"] = f"SSH connection failed: {e}"
        print(f"[{ip}] ERROR: {status['error']}")
        return status

    try:
        sftp = client.open_sftp()
        print(f"[{ip}] Uploading '{local_file}' to {remote_folder}")

        remote_path = upload_file(sftp, local_file, remote_folder)
        status["uploaded"] = True
        status["remote_path"] = remote_path

        print(f"[{ip}] SUCCESS: File uploaded to {remote_path}")

        sftp.close()
    except Exception as e:
        status["error"] = f"Upload failed: {e}"
        print(f"[{ip}] ERROR: {status['error']}")
    finally:
        client.close()
        print(f"[{ip}] Connection closed.")

    return status


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 upload_single_file.py <file_to_upload>")
        sys.exit(1)

    local_file = sys.argv[1]

    if not os.path.isfile(local_file):
        print(f"ERROR: '{local_file}' is not a file.")
        sys.exit(1)

    cfg = load_config()
    username = cfg["username"]
    password = cfg["password"]
    targets = cfg["targets"]

    remote_folder = f"/home/{username}/Info_Gathering_JSONS_And_DeepScans"

    print(f"Loaded {len(targets)} targets.")
    print(f"Local file: {local_file}")
    print(f"Remote folder: {remote_folder}")

    results = []

    for ip in targets:
        result = deploy_to_host(ip, username, password, local_file, remote_folder)
        results.append(result)

    print("\n================ FINAL REPORT ================\n")

    for r in results:
        print(f"Host: {r['ip']}")
        print(f"  Connected: {r['connected']}")
        print(f"  Uploaded:  {r['uploaded']}")
        print(f"  Remote Path: {r['remote_path']}")
        print(f"  Error: {r['error']}")
        print("")


if __name__ == "__main__":
    main()