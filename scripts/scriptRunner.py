import os
import sys
import signal
import subprocess
from tqdm import tqdm

TIMEOUT_SECS = 600  # 10 minutes

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

def run_with_timeout(owner_repo: str) -> None:
    is_windows = os.name == "nt"

    popen_kwargs = {
        "args": ["python3", "findUCBBC.py", owner_repo],
        "stdin": None,
        "stdout": None,
        "stderr": None,
        "text": False,
    }

    if is_windows:
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["preexec_fn"] = os.setsid

    proc = subprocess.Popen(**popen_kwargs)
    try:
        proc.communicate(timeout=TIMEOUT_SECS)
    except subprocess.TimeoutExpired:
        print(f"Timeout: {owner_repo} exceeded {TIMEOUT_SECS} seconds. Killing process group...")

        if is_windows:
            try:
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            except Exception:
                pass
            try:
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/F", "/T"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        else:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            if is_windows:
                try:
                    subprocess.run(["taskkill", "/PID", str(proc.pid), "/F", "/T"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
            else:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

        print(f"Skipped: {owner_repo}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scriptRunner.py <input_file>")
        return

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    try:
        for owner_repo in tqdm(lines, desc="Processing repos"):
            print(f"Running script for: {owner_repo}")
            run_with_timeout(owner_repo)
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")

if __name__ == "__main__":
    main()
