def convert_transaction_to_symbol(transaction):
    symbols = []

    if transaction["amount"] >= 10000:
        symbols.append("H")
    else:
        symbols.append("L")

    if transaction["location"].lower() == "foreign":
        symbols.append("F")

    if transaction["type"].lower() == "withdrawal":
        symbols.append("W")
    else:
        symbols.append("P")

    return "".join(symbols)


def preprocess_transactions(transactions):
    result = []

    for transaction in transactions:
        symbol = convert_transaction_to_symbol(transaction)

        item = transaction.copy()
        item["symbol"] = symbol

        result.append(item)

    return result