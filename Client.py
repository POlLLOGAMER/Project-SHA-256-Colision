import hashlib
import os
import time
import csv
import webbrowser
from datetime import datetime
import subprocess

REPO_FORK = "https://huggingface.co/datasets/<user>/SHA-256-Proyect"
REPO_ORIGINAL = "https://huggingface.co/datasets/PolloLOL/SHA-256-Proyect"
REPO_DIR = "SHA-256-Proyect"
CSV_FILE = os.path.join(REPO_DIR, "collisions.csv")


def clone_or_pull():
    if not os.path.exists(REPO_DIR):
        subprocess.run(["git", "clone", REPO_FORK])
    else:
        subprocess.run(["git", "-C", REPO_DIR, "pull"])


def append_and_commit(input1, input2, hash_val, collision_type):
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    branch = f"collision-{timestamp}"
    subprocess.run(["git", "-C", REPO_DIR, "checkout", "-b", branch])

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([input1, input2, hash_val, collision_type])

    subprocess.run(["git", "-C", REPO_DIR, "add", "collisions.csv"])
    subprocess.run(["git", "-C", REPO_DIR, "commit", "-m", f"Add {collision_type} collision at {timestamp}"])
    subprocess.run(["git", "-C", REPO_DIR, "push", "--set-upstream", "origin", branch])

    print("[✓] Collision committed and pushed!")
    open_pr_link(branch)


def open_pr_link(branch):
    pr_url = f"{REPO_FORK}/pull/new/{branch}"
    print(f"[→] Open this URL to create a pull request: {pr_url}")
    webbrowser.open(pr_url)


def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()


def increment_string(s):
    charset = "abcdefghijklmnopqrstuvwxyz0123456789"
    s = list(s)
    i = len(s) - 1
    while i >= 0:
        if s[i] == charset[-1]:
            s[i] = charset[0]
            i -= 1
        else:
            s[i] = charset[charset.index(s[i]) + 1]
            break
    return ''.join(s)


def process_range(start, end, target_suffix="deadbe"):
    hash_dict = {}
    current = start
    while current <= end:
        h = sha256(current)
        if h in hash_dict and hash_dict[h] != current:
            append_and_commit(hash_dict[h], current, h, "total")
        if h.endswith(target_suffix):
            append_and_commit(current, current, h, "partial")
        hash_dict[h] = current
        current = increment_string(current)


if __name__ == "__main__":
    print("[+] Client started with PR support...")
    clone_or_pull()
    process_range("aaa", "aaf")
