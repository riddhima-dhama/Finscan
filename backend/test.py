from automata.fraud_engine import detect_fraud


transactions = [
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


print("\nFINSCAN FRAUD DETECTION TEST\n")

for item in transactions:

    result = detect_fraud(item["data"])

    print("=" * 45)
    print("Transaction:", item["name"])
    print("Generated Symbols:", result["symbols"])
    print("Fraud Detected:", result["is_fraud"])

    if result["matched_rules"]:
        print("Matched Rules:")

        for rule in result["matched_rules"]:
            print("-", rule["rule"])
            print("  Pattern:", rule["pattern"])

    else:
        print("Matched Rules: None")

print("=" * 45)