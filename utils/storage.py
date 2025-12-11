import json
import os

DATA_FILE = "data/properties.json"

# Ensure file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_properties():
    """Load all saved properties from JSON file."""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_property(property_id, data):
    """Save or update property under its ID."""
    properties = load_properties()
    properties[property_id] = data

    with open(DATA_FILE, "w") as f:
        json.dump(properties, f, indent=2)

def get_property(property_id):
    """Retrieve saved property by ID."""
    properties = load_properties()
    return properties.get(property_id, None)

def list_properties():
    """List all saved property keys."""
    return list(load_properties().keys())
