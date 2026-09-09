from flask import Flask, jsonify, request
from flask_cors import CORS
import json

from preprocessing import preprocess_transactions

app = Flask(__name__)
CORS(app)


# -----------------------------
# Load transaction dataset
# -----------------------------

def load_transactions():
    with open("transactions.json", "r") as file:
        return json.load(file)


# -----------------------------
# Home
# -----------------------------

@app.route("/")
def home():
    return jsonify({
        "message": "FinScan Backend is Running"
    })


# -----------------------------
# Get all transactions
# -----------------------------

@app.route("/api/transactions", methods=["GET"])
def get_transactions():

    transactions = load_transactions()

    processed = preprocess_transactions(transactions)

    return jsonify(processed)


# -----------------------------
# Detect fraud
# -----------------------------

@app.route("/api/detect", methods=["POST"])
def detect_fraud():

    data = request.get_json()

    transactions = data.get("transactions", [])

    processed = preprocess_transactions(transactions)

    symbols = [item["symbol"] for item in processed]

    # Temporary detection logic
    # This will later be replaced by Person 1's
    # actual DFA / fraud detection engine.

    fraud = False
    rule = "No fraud detected"

    for item in processed:

        if "HF" in item["symbol"]:
            fraud = True
            rule = "High-value foreign transaction"
            break

    return jsonify({
        "fraud": fraud,
        "rule": rule,
        "symbols": symbols,
        "transactions": processed
    })


# -----------------------------
# Statistics
# -----------------------------

@app.route("/api/stats", methods=["GET"])
def get_stats():

    transactions = load_transactions()

    processed = preprocess_transactions(transactions)

    total = len(processed)

    fraud_count = 0

    for transaction in processed:
        if "HF" in transaction["symbol"]:
            fraud_count += 1

    normal_count = total - fraud_count

    return jsonify({
        "total": total,
        "normal": normal_count,
        "fraud": fraud_count
    })


# -----------------------------
# Run server
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)