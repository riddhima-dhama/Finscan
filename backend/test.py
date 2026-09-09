from automata.symbols import transaction_to_symbols
from automata.fraud_rules import FRAUD_RULES


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


print("\nTRANSACTION SYMBOL TEST\n")

for item in transactions:
    symbols = transaction_to_symbols(item["data"])

    print(f"Transaction: {item['name']}")
    print(f"Symbols: {symbols}")
    print("-" * 35)


print("\nFRAUD RULES\n")

for rule, details in FRAUD_RULES.items():
    print(f"{rule}: {details['pattern']}")