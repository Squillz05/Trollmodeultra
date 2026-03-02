#!/usr/bin/env python3

import json
import subprocess
import datetime

CONFIG_FILE = "config4.json"
OUTPUT_FILE = "blue_whatweb_results.json"


def load_targets():
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    return data["targets"]


def run_whatweb(ip):
    try:
        cmd = [
            "whatweb",
            "--aggression=3",
            "--color=never",
            f"http://{ip}"
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        output = result.stdout.strip()

        if output:
            return output
        return None

    except Exception as e:
        return None


def main():
    targets = load_targets()
    results = {}

    print(f"Loaded {len(targets)} Blue Team targets.")
    print("Starting aggressive whatweb scan...\n")

    for ip in targets:
        print(f"Scanning {ip} ...")
        output = run_whatweb(ip)

        if output:
            print(f"  [+] Found web info on {ip}")
            results[ip] = output
        else:
            print(f"  [-] No web response from {ip}")

    print("\nSaving results...")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Done. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
