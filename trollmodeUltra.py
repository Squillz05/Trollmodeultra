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


def upload_tooling(client):
    """Upload trollmode1.py and modules/ to remote home directory."""
    sftp = client.open_sftp()

    # Upload trollmode1.py
    sftp.put("trollmode1.py", "/home/dbadmin/trollmode1.py")

    # Upload modules directory
    sftp_upload_dir(sftp, "modules", "/home/dbadmin/modules")

    sftp.close()


def run_remote_scan(client, ip):
    """Runs trollmode1.py on the remote host."""
    cmd = f"python3 /home/dbadmin/trollmode1.py --ip {ip}"
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.channel.recv_exit_status()

    return f"/home/dbadmin/{ip}.json"


def scp_file(client, remote_path, local_path):
    sftp = client.open_sftp()
    sftp.get(remote_path, local_path)
    sftp.close()


def cleanup_remote(client, ip):
    """Delete trollmode1.py, modules/, and the output JSON."""
    cleanup_cmds = [
        "rm -f /home/dbadmin/trollmode1.py",
        "rm -rf /home/dbadmin/modules",
        f"rm -f /home/dbadmin/{ip}.json"
    ]

    for cmd in cleanup_cmds:
        client.exec_command(cmd)


def main():
    cfg = load_config()

    username = cfg["username"]
    password = cfg["password"]
    targets = cfg["targets"]

    print(f"Loaded {len(targets)} targets")

    for ip in targets:
        print(f"\n--- Connecting to {ip} ---")

        try:
            client = ssh_connect(ip, username, password)
            print(f"Connected to {ip}")

        except Exception as e:
            print(f"FAILED to connect to {ip}: {e}")
            print("Skipping this host.")
            continue  # move to next IP

        try:
            print("Uploading tooling...")
            upload_tooling(client)

            print("Running remote trollmode1.py...")
            remote_json_path = run_remote_scan(client, ip)

            local_filename = f"{ip}.json"
            print(f"Downloading {local_filename} ...")
            scp_file(client, remote_json_path, local_filename)

            print(f"Successfully pulled {local_filename}")

        except Exception as e:
            print(f"ERROR running scan on {ip}: {e}")

        finally:
            print(f"Cleaning up remote files on {ip}...")
            try:
                cleanup_remote(client, ip)
            except Exception as e:
                print(f"Cleanup failed on {ip}: {e}")

            try:
                client.close()
            except:
                pass

            print(f"Finished processing {ip}")


if __name__ == "__main__":
    main()