from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os

# Objective 1: Fetch data from backend and send it to frontend
app = FastAPI()

# Middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DATA_FILE = "data.json"
USER_DATA_FILE = "user_data.json"

# Objective 2: Handling missing or invalid data when loading data from the backend
def load_data(file_path):
    """Safely loads JSON data from the given file, returning a fallback if there's an issue."""
    if not os.path.exists(file_path):
        return {"medicines": []}
    
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            if not isinstance(data, dict) or "medicines" not in data or not isinstance(data["medicines"], list):
                return {"medicines": []}
            return data
    except (json.JSONDecodeError, IOError):
        return {"medicines": []}

# Function to save user data
def save_user_data(data):
    """Saves user-entered medicines in `user_data.json`."""
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Objective 1: Route to get all medicines (merged base + user data)
@app.get("/medicines")
def get_all_meds():
    base_data = load_data(BASE_DATA_FILE)
    user_data = load_data(USER_DATA_FILE)
    all_medicines = base_data["medicines"] + user_data["medicines"]

    # Handling missing or invalid data
    for med in all_medicines:
        if "name" not in med or not med["name"]:
            med["name"] = "No Name Provided"
        if "price" not in med or med["price"] is None or med["price"] == "":
            med["price"] = None  # Let frontend handle the display

    return {"medicines": all_medicines}

# Objective 3: Route to create a new medicine entry (only in `user_data.json`)
@app.post("/create")
def create_med(name: str = Form(...), price: str = Form(...)):
    """Adds a new medicine to `user_data.json`, keeping base data unchanged."""
    user_data = load_data(USER_DATA_FILE)

    new_med = {
        "name": name.strip() if name.strip() else "No Name Provided",
        "price": float(price) if price and price.replace(".", "", 1).isdigit() else None
    }

    user_data["medicines"].append(new_med)
    save_user_data(user_data)

    return {"message": f"Medicine '{name}' added successfully."}

# Objective 4: Route to update a medicine's price (only in `user_data.json`)
@app.post("/update")
def update_med(name: str = Form(...), price: str = Form(...)):
    """Updates the price of a user-entered medicine."""
    user_data = load_data(USER_DATA_FILE)
    
    for med in user_data["medicines"]:
        if med.get("name") == name:
            med["price"] = float(price) if price and price.replace(".", "", 1).isdigit() else None
            save_user_data(user_data)
            return {"message": f"Medicine '{name}' updated successfully."}

    return {"error": "Medicine not found in user data"}


@app.delete("/delete")
def delete_med(name: str = Form(...)):
    """Deletes a user-entered medicine, leaving base data untouched."""
    user_data = load_data(USER_DATA_FILE)

    for med in user_data["medicines"]:
        if med.get("name") == name:
            user_data["medicines"].remove(med)
            save_user_data(user_data)
            return {"message": f"Medicine '{name}' deleted successfully."}

    return {"error": "Medicine not found in user data"}

# Objective 5: Create a backend function for averaging prices of all medicines
@app.get("/average_price")
def get_average_price():
    """Calculates the average price of all medicines."""
    all_medicines = get_all_meds()["medicines"]
    
    # Filter out medicines with no price or invalid price
    valid_prices = [med["price"] for med in all_medicines if med["price"] is not None]
    
    if not valid_prices:
        return {"average_price": "No valid prices available"}

    average_price = sum(valid_prices) / len(valid_prices)
    
    return {"average_price": round(average_price, 2)}

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
