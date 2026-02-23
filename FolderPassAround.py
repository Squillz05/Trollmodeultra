#!/usr/bin/env python3

import json
import os
import paramiko


def load_config():
    with open("config2.json", "r") as f:
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


def sftp_upload_dir(sftp, local_dir, remote_dir):
    """Recursively upload a directory."""
    try:
        sftp.mkdir(remote_dir)
    except IOError:
        pass  # already exists

    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir + "/" + item

        if os.path.isdir(local_path):
            sftp_upload_dir(sftp, local_path, remote_path)
        else:
            sftp.put(local_path, remote_path)


def deploy_to_host(ip, username, password, local_folder, remote_folder):
    print(f"\n--- Connecting to {ip} ---")

    try:
        client = ssh_connect(ip, username, password)
        print(f"Connected to {ip}")
    except Exception as e:
        print(f"FAILED to connect to {ip}: {e}")
        return

    try:
        sftp = client.open_sftp()
        print(f"Uploading folder '{local_folder}' → {remote_folder}")
        sftp_upload_dir(sftp, local_folder, remote_folder)
        sftp.close()
        print(f"SUCCESS: Uploaded to {ip}")
    except Exception as e:
        print(f"ERROR uploading to {ip}: {e}")
    finally:
        client.close()
        print(f"Finished {ip}")


def main():
    cfg = load_config()
    username = cfg["username"]
    password = cfg["password"]
    targets = cfg["targets"]

    local_folder = "Info_Gathering_JSONS_And_DeepScans"
    remote_folder = "/home/" + username + "/Info_Gathering_JSONS_And_DeepScans"

    print(f"Loaded {len(targets)} targets.")

    for ip in targets:
        deploy_to_host(ip, username, password, local_folder, remote_folder)


if __name__ == "__main__":
    main()