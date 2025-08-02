import hashlib
import os
import csv
import subprocess
import webbrowser
import random
from datetime import datetime

REPO_FORK = "https://huggingface.co/datasets/<your_user>/SHA-256-Proyect"  # <-- put your HF fork URL here
REPO_DIR = "SHA-256-Proyect"
CSV_FILE = os.path.join(REPO_DIR, "collisions.csv")

def clone_or_pull():
    if not os.path.exists(REPO_DIR):
        subprocess.run(["git", "clone", REPO_FORK])
        print("[+] Fork cloned!")
    else:
        subprocess.run(["git", "-C", REPO_DIR, "pull"])
        print("[+] Fork updated!")

def load_existing_inputs():
    inputs = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                inputs.add(row[0])
                inputs.add(row[1])
    return inputs

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

def random_string(min_len=3, max_len=15):
    charset = "abcdefghijklmnopqrstuvwxyz0123456789"
    length = random.randint(min_len, max_len)
    return ''.join(random.choice(charset) for _ in range(length))

def main(target_suffix="deadbe", min_len=3, max_len=15):
    print("[+] Fully randomized client with PR support and smart skipping...")
    clone_or_pull()
    existing_inputs = load_existing_inputs()
    hash_dict = {}
    tried = set()
    while True:
        candidate = random_string(min_len, max_len)
        if candidate in existing_inputs or candidate in tried:
            continue
        h = sha256(candidate)
        if h in hash_dict and hash_dict[h] != candidate:
            print(f"[!!!] Total collision found:")
            print(f"    {hash_dict[h]} and {candidate} => {h}")
            append_and_commit(hash_dict[h], candidate, h, "total")
            break
        if h.endswith(target_suffix):
            print(f"[!!!] Partial collision found: {candidate} => {h}")
            append_and_commit(candidate, candidate, h, "partial")
        hash_dict[h] = candidate
        tried.add(candidate)

if __name__ == "__main__":
    main(target_suffix="deadbe", min_len=3, max_len=15)
