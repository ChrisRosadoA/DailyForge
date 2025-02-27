import json

# Load the data once when the module is first imported
def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}}

# Save the data when called
def save_data():
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

# Initialize data (runs once on import)
data = load_data()
