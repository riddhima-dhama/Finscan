from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

from preprocessing import preprocess_transactions
from automata.fraud_engine import detect_fraud as run_fraud_engine
from automata.visualizer import build_automata_visualization


app = Flask(__name__)

CORS(app)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# LOAD TRANSACTIONS
# =========================================================

def load_transactions():

    file_path = os.path.join(
        BASE_DIR,
        "transactions.json"
    )

    with open(file_path, "r") as file:

        return json.load(file)


# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message":
            "FinScan Backend is Running"
    })


# =========================================================
# TRANSACTIONS
# =========================================================

@app.route(
    "/api/transactions",
    methods=["GET"]
)
def get_transactions():

    try:

        transactions = load_transactions()

        processed = preprocess_transactions(
            transactions
        )

        return jsonify(processed)

    except Exception as error:

        print(
            "Transaction error:",
            error
        )

        return jsonify({
            "error": str(error)
        }), 500


# =========================================================
# FRAUD DETECTION
# =========================================================

@app.route(
    "/api/detect",
    methods=["POST"]
)
def detect_fraud():

    try:

        data = request.get_json() or {}

        transactions = data.get(
            "transactions",
            []
        )

        results = []

        for transaction in transactions:

            result = run_fraud_engine(
                transaction
            )

            results.append({

                "transaction":
                    transaction,

                "symbols":
                    result.get(
                        "symbols",
                        ""
                    ),

                "fraud":
                    result.get(
                        "is_fraud",
                        False
                    ),

                "matched_rules":
                    result.get(
                        "matched_rules",
                        []
                    ),

                "execution_trace":
                    result.get(
                        "execution_trace",
                        []
                    )

            })


        # =================================================
        # OVERALL FRAUD
        # =================================================

        fraud_transactions = [

            item

            for item in results

            if item["fraud"]

        ]

        fraud = (
            len(fraud_transactions) > 0
        )


        # =================================================
        # MATCHED RULE NAMES
        # =================================================

        matched_rule_names = []

        for item in fraud_transactions:

            for rule in item["matched_rules"]:

                if isinstance(
                    rule,
                    dict
                ):

                    name = rule.get(
                        "rule",
                        ""
                    )

                else:

                    name = str(rule)

                if (
                    name
                    and
                    name not in
                    matched_rule_names
                ):

                    matched_rule_names.append(
                        name
                    )


        if matched_rule_names:

            rule_text = ", ".join(
                matched_rule_names
            )

        else:

            rule_text = (
                "No fraud detected"
            )


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "fraud":
                fraud,

            "rule":
                rule_text,

            "symbols": [

                item["symbols"]

                for item in results

            ],

            "transactions":
                results

        })


    except Exception as error:

        print(
            "Detection error:",
            error
        )

        return jsonify({

            "error":
                str(error)

        }), 500


# =========================================================
# STATISTICS
# =========================================================

@app.route(
    "/api/stats",
    methods=["GET"]
)
def get_stats():

    try:

        transactions = load_transactions()

        total = len(transactions)

        fraud_count = 0

        for transaction in transactions:

            result = run_fraud_engine(
                transaction
            )

            if result.get(
                "is_fraud",
                False
            ):

                fraud_count += 1


        normal_count = (
            total - fraud_count
        )


        return jsonify({

            "total":
                total,

            "normal":
                normal_count,

            "fraud":
                fraud_count

        })


    except Exception as error:

        print(
            "Stats error:",
            error
        )

        return jsonify({

            "error":
                str(error)

        }), 500


# =========================================================
# AUTOMATA RULES
# =========================================================

@app.route(
    "/api/automata-diagram",
    methods=["GET"]
)
def get_automata_diagram():

    try:

        from automata.fraud_rules import FRAUD_RULES

        rules = []

        for name, data in FRAUD_RULES.items():

            rules.append({

                "name":
                    name,

                "pattern":
                    data["pattern"],

                "description":
                    data["description"]

            })


        return jsonify({
            "rules": rules
        })


    except Exception as error:

        return jsonify({

            "error":
                str(error)

        }), 500


# =========================================================
# AUTOMATA VISUALIZER
# =========================================================

@app.route(
    "/api/automata/visualize",
    methods=["POST"]
)
def visualize_automata():

    try:

        data = request.get_json() or {}

        regex = data.get(
            "regex",
            ""
        ).strip()


        if not regex:

            return jsonify({

                "error":
                    "Regex is required."

            }), 400


        result = build_automata_visualization(
            regex
        )


        return jsonify(result)


    except Exception as error:

        print(
            "Automata error:",
            error
        )

        return jsonify({

            "error":
                str(error)

        }), 400


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )