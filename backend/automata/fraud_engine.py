from automata.symbols import transaction_to_symbols
from automata.fraud_rules import FRAUD_RULES
from automata.regex_to_nfa import regex_to_nfa
from automata.nfa_to_dfa import nfa_to_dfa
from automata.dfa_minimizer import minimize_dfa


def run_dfa(dfa, input_string):
    current_state = dfa["start_state"]

    for symbol in input_string:
        transitions = dfa["transitions"].get(current_state, {})

        if symbol not in transitions:
            return False

        current_state = transitions[symbol]

    return current_state in dfa["accept_states"]


def build_rule_dfa(pattern):
    nfa = regex_to_nfa(pattern)
    dfa = nfa_to_dfa(nfa)
    minimized_dfa = minimize_dfa(dfa)

    return minimized_dfa


def detect_fraud(transaction):
    symbols = transaction_to_symbols(transaction)

    matched_rules = []

    for rule_name, rule_data in FRAUD_RULES.items():
        pattern = rule_data["pattern"]

        try:
            dfa = build_rule_dfa(pattern)

            if run_dfa(dfa, symbols):
                matched_rules.append({
                    "rule": rule_name,
                    "pattern": pattern,
                    "description": rule_data["description"]
                })

        except Exception as error:
            print(f"Error processing rule {rule_name}: {error}")

    return {
        "symbols": symbols,
        "is_fraud": len(matched_rules) > 0,
        "matched_rules": matched_rules
    }


if __name__ == "__main__":

    test_transactions = [
        {
            "name": "Normal Transaction",
            "data": {
                "amount": 5000,
                "country": "India",
                "time": "14:30",
                "repeated": False,
                "transaction_type": "Online"
            }
        },
        {
            "name": "High Foreign Transaction",
            "data": {
                "amount": 80000,
                "country": "USA",
                "time": "14:30",
                "repeated": False,
                "transaction_type": "Online"
            }
        },
        {
            "name": "Critical Fraud Transaction",
            "data": {
                "amount": 90000,
                "country": "USA",
                "time": "02:30",
                "repeated": True,
                "transaction_type": "Online"
            }
        }
    ]

    for item in test_transactions:

        result = detect_fraud(item["data"])

        print("\n" + "=" * 45)
        print("Transaction:", item["name"])
        print("Symbols:", result["symbols"])
        print("Fraud Detected:", result["is_fraud"])

        if result["matched_rules"]:
            print("\nMatched Rules:")

            for rule in result["matched_rules"]:
                print("-", rule["rule"])
                print("  Pattern:", rule["pattern"])
                print("  Description:", rule["description"])

        else:
            print("No fraud rule matched.")