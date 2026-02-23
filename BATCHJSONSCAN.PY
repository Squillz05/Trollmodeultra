#!/usr/bin/env python3

import os
import sys
import json
from JSONScan import load_scan, analyze   


def save_report(findings, output_path):
    try:
        with open(output_path, "w") as f:
            json.dump(findings, f, indent=4)
        return True
    except Exception as e:
        print(f"ERROR saving report to {output_path}: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 BatchJSONScan.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    os.makedirs(output_folder, exist_ok=True)

    print(f"\n📁 Input folder:  {input_folder}")
    print(f"📁 Output folder: {output_folder}\n")

    files = [f for f in os.listdir(input_folder) if f.endswith(".json")]

    if not files:
        print("No JSON files found in input folder.")
        sys.exit(1)

    for filename in files:
        print(f"🔍 Scanning: {filename}")

        input_path = os.path.join(input_folder, filename)

        try:
            scan = load_scan(input_path)
            findings = analyze(scan)

            # Build output filename: <original>_PARSESCAN.json
            base = filename.replace(".json", "")
            output_name = f"{base}_PARSESCAN.json"
            output_path = os.path.join(output_folder, output_name)

            if save_report(findings, output_path):
                print(f"   ✅ Success → {output_name} ({len(findings)} findings)")
            else:
                print(f"   ❌ Failed to save output for {filename}")

        except Exception as e:
            print(f"   ❌ ERROR processing {filename}: {e}")

    print("\nBatch scan complete.\n")


if __name__ == "__main__":
    main()