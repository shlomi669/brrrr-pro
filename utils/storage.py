import os
import json

DATA_DIR = "data"

def save_property_snapshot(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{filename}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    return f"{filename}.json"

def list_snapshots():
    """Return list of snapshot filenames (without .json extension)."""
    if not os.path.exists(DATA_DIR):
        return []
    files = [f.replace(".json", "") for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    return sorted(files)

def load_snapshot(filename):
    """Load a snapshot file by name (without .json extension)."""
    path = os.path.join(DATA_DIR, f"{filename}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def load_last_snapshot():
    """Return the newest snapshot based on modification time."""
    if not os.path.exists(DATA_DIR):
        return None
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    if not files:
        return None
    newest = max(files, key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)))
    with open(os.path.join(DATA_DIR, newest), "r") as f:
        return json.load(f)
