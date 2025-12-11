import json
import os

DATA_DIR = "data"

# Make sure data folder exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def save_property_snapshot(name: str, data: dict):
    """Saves a property snapshot to a JSON file."""
    filename = os.path.join(DATA_DIR, f"{name}.json")
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    return filename


def load_property_snapshot(name: str):
    """Loads a saved property snapshot by name."""
    filename = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        return json.load(f)


def list_saved_snapshots():
    """Returns list of saved property snapshot files."""
    files = os.listdir(DATA_DIR)
    return [f.replace(".json", "") for f in files if f.endswith(".json")]
