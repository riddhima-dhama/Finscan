from flask import Flask, jsonify, request
from flask_cors import CORS
import json

from preprocessing import preprocess_transactions
from automata.fraud_engine import detect_fraud as run_fraud_engine

app = Flask(__name__)
CORS(app)


def load_transactions():
    with open("transactions.json", "r") as file:
        return json.load(file)


@app.route("/")
def home():
    return jsonify({
        "message": "FinScan Backend is Running"
    })


@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    transactions = load_transactions()
    processed = preprocess_transactions(transactions)
    return jsonify(processed)


@app.route("/api/detect", methods=["POST"])
def detect_fraud():
    data = request.get_json() or {}
    transactions = data.get("transactions", [])

    results = []
    for transaction in transactions:
        result = run_fraud_engine(transaction)
        results.append({
            "transaction": transaction,
            "symbols": result["symbols"],
            "fraud": result["is_fraud"],
            "matched_rules": result["matched_rules"]
        })

    fraud_transactions = [r for r in results if r["fraud"]]
    fraud = len(fraud_transactions) > 0

    matched_rule_names = []
    for result in fraud_transactions:
        for r in result["matched_rules"]:
            name = r.get("rule", str(r)) if isinstance(r, dict) else str(r)
            if name not in matched_rule_names:
                matched_rule_names.append(name)

    rule = ", ".join(matched_rule_names) if matched_rule_names else "No fraud detected"

    return jsonify({
        "fraud": fraud,
        "rule": rule,
        "symbols": [s for res in results for s in res["symbols"]],
        "transactions": results
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    transactions = load_transactions()
    total = len(transactions)
    fraud_count = 0

    for transaction in transactions:
        result = run_fraud_engine(transaction)
        if result["is_fraud"]:
            fraud_count += 1

    normal_count = total - fraud_count

    return jsonify({
        "total": total,
        "normal": normal_count,
        "fraud": fraud_count
    })



@app.route("/api/automata-diagram", methods=["GET"])
def get_automata_diagram():
    from automata.fraud_rules import FRAUD_RULES
    rules = []
    for name, data in FRAUD_RULES.items():
        rules.append({
            "name": name,
            "pattern": data["pattern"],
            "description": data["description"]
        })
    states = [
        {"id": "q0", "label": "q0 (Start)", "is_final": False},
        {"id": "q1", "label": "q1 (High Val)", "is_final": False},
        {"id": "q2", "label": "q2 (Fraud Trap)", "is_final": True}
    ]
    transitions = [
        {"from": "q0", "to": "q0", "symbol": "L / M"},
        {"from": "q0", "to": "q1", "symbol": "H"},
        {"from": "q1", "to": "q2", "symbol": "F / O / R"},
        {"from": "q1", "to": "q0", "symbol": "L"},
        {"from": "q2", "to": "q2", "symbol": "*"}
    ]
    return jsonify({"rules": rules, "states": states, "transitions": transitions})

if __name__ == "__main__":
    app.run(debug=True, port=5001)