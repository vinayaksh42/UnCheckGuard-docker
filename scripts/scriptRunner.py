import subprocess
import os
import sys
from tqdm import tqdm

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scriptRunner.py <input_file>")
        return

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # Read all lines
    with open(file_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Process each repo with a progress bar
    for owner_repo in tqdm(lines, desc="Processing repos"):
        print(f"Running script for: {owner_repo}")
        subprocess.run(["python3", "findUCBBC.py", owner_repo])

if __name__ == "__main__":
    main()