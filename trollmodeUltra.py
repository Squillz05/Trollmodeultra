#!/usr/bin/env python3

import json
import os
import paramiko


def load_config():
    with open("config1.json", "r") as f:
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


def run_remote_scan(client, remote_tool_path, remote_output_dir, ip):
    """
    Runs trollmode1.py on the remote host.
    Returns the path to the generated JSON file.
    """

    # Ensure output directory exists (home dir always exists, but safe)
    client.exec_command(f"mkdir -p {remote_output_dir}")

    # Run the tool with IP-based naming
    cmd = f"python3 {remote_tool_path} --ip {ip}"
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.channel.recv_exit_status()  # Wait for completion

    # The file should be named <ip>.json in the home directory
    remote_json = os.path.join(remote_output_dir, f"{ip}.json")
    return remote_json


def scp_file(client, remote_path, local_path):
    sftp = client.open_sftp()
    sftp.get(remote_path, local_path)
    sftp.close()


def main():
    cfg = load_config()

    username = cfg["username"]
    password = cfg["password"]
    targets = cfg["targets"]

    remote_tool_path = cfg["remote_tool_path"]
    remote_output_dir = cfg["remote_output_dir"]

    print(f"Loaded {len(targets)} targets")

    for ip in targets:
        print(f"\n--- Connecting to {ip} ---")

        try:
            client = ssh_connect(ip, username, password)
            print(f"Connected to {ip}")

            print("Running remote trollmode1.py...")
            remote_json_path = run_remote_scan(client, remote_tool_path, remote_output_dir, ip)

            local_filename = f"{ip}.json"
            print(f"Downloading {local_filename} ...")
            scp_file(client, remote_json_path, local_filename)

            print(f"Successfully pulled {local_filename}")

        except Exception as e:
            print(f"ERROR on {ip}: {e}")

        finally:
            try:
                client.close()
            except:
                pass


if __name__ == "__main__":
    main()