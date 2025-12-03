from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import logging

import certifi

from hardware import hardwareSet

load_dotenv()

LOG = logging.getLogger("resource_service")
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
CORS(app, supports_credentials=True)

# Config via env
MONGO_URI = os.getenv("MONGO_URI")
RESOURCE_DB = os.getenv("RESOURCE_DB", "resource-management-db")
RESOURCES_COLLECTION = os.getenv("RESOURCES_COLLECTION", "resources")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
resources_collection = client[RESOURCE_DB][RESOURCES_COLLECTION] if client else None

if not MONGO_URI:
    LOG.warning("MONGO_URI not set - database won't be available until configured.")

client = MongoClient(MONGO_URI) if MONGO_URI else None
resources_collection = client[RESOURCE_DB][RESOURCES_COLLECTION] if client else None

# hardware helper
hardware_set = hardwareSet()


@app.route("/", methods=["GET"])
def root():
    return jsonify({"service": "resource-service", "status": "ok"})


@app.route("/hardware/<int:hardware_id>/capacity", methods=["GET"])
def get_hardware_capacity(hardware_id):
    if resources_collection is None:
        return jsonify({"error": "Database not configured"}), 500
    hardware = resources_collection.find_one({"hardware_id": hardware_id}, {"_id": 0, "total_capacity": 1})
    if hardware:
        hardware["hardware_id"] = hardware_id
        hardware_set.initialize_capacity(hardware)
        capacity = hardware_set.get_capacity()
        return jsonify({"capacity": capacity})
    return jsonify({"error": "Hardware not found"}), 404


@app.route("/hardware/<int:hardware_id>/availability", methods=["GET"])
def get_hardware_availability(hardware_id):
    if resources_collection is None:
        return jsonify({"error": "Database not configured"}), 500
    hardware = resources_collection.find_one({"hardware_id": hardware_id}, {"_id": 0, "available": 1})
    if hardware:
        hardware["hardware_id"] = hardware_id
        hardware_set.initialize_availability(hardware)
        availability = hardware_set.get_availability()
        return jsonify({"availability": availability})
    return jsonify({"error": "Hardware not found"}), 404


@app.route("/hardware/checkout", methods=["POST"])
def checkout_hardware():
    if resources_collection is None:
        return jsonify({"error": "Database not configured"}), 500
    data = request.get_json() or {}
    qty = data.get("qty")
    project_id = data.get("project_id")
    hardware_id = data.get("hardware_id")

    if qty is None or project_id is None or hardware_id is None:
        return jsonify({"error": "Missing required fields: qty, project_id, hardware_id"}), 400

    result, updated_availability = hardware_set.check_out(qty, project_id, hardware_id)

    hardware = resources_collection.find_one({"hardware_id": hardware_id})
    if not hardware:
        return jsonify({"error": "Hardware not found"}), 400

    resources_collection.update_one({"hardware_id": hardware_id}, {"$set": {"available": updated_availability}})

    if result == -1:
        return jsonify({"error": "No units available for checkout"}), 400
    elif result == 1:
        return jsonify({"message": "Only partial checkout completed.", "available": updated_availability}), 200
    elif result == 0:
        return jsonify({"message": "Checkout successful.", "available": updated_availability}), 200
    else:
        return jsonify({"message": "Unexpected checkout case.", "available": updated_availability}), 500


@app.route("/hardware/checkin", methods=["POST"])
def checkin_hardware():
    if resources_collection is None:
        return jsonify({"error": "Database not configured"}), 500
    data = request.get_json() or {}
    qty = data.get("qty")
    project_id = data.get("project_id")
    hardware_id = data.get("hardware_id")

    if qty is None or project_id is None or hardware_id is None:
        return jsonify({"error": "Missing required fields: qty, project_id, hardware_id"}), 400

    result, updated_availability = hardware_set.check_in(qty, project_id, hardware_id)

    if result in [0, 1]:
        resources_collection.update_one({"hardware_id": hardware_id}, {"$set": {"available": updated_availability}})

    if result == -1:
        return jsonify({"error": "Project never checked anything out."}), 400
    elif result == -2:
        return jsonify({"error": "Nothing to check in for this project and hardware."}), 400
    elif result == -3:
        return jsonify({"error": "You cannot check in more than capacity."}), 400
    elif result == -4:
        return jsonify({"error": "You cannot check in < 0"}), 400
    elif result == 1:
        return jsonify({"message": "Partial check-in completed.", "available": updated_availability}), 200
    elif result == 0:
        return jsonify({"message": "Check-in successful.", "available": updated_availability}), 200
    else:
        return jsonify({"error": "Unexpected error during check-in."}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
