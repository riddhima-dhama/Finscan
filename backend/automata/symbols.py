def transaction_to_symbols(transaction, home_country="India"):
    symbols = []

    amount = transaction.get("amount", 0)

    if amount > 50000:
        symbols.append("H")
    elif amount >= 10000:
        symbols.append("M")
    else:
        symbols.append("L")

    country = transaction.get("country", home_country)

    if country.lower() != home_country.lower():
        symbols.append("F")

    time_value = transaction.get("time")

    if time_value:
        try:
            hour = int(str(time_value).split(":")[0])

            if 0 <= hour < 5:
                symbols.append("O")
        except (ValueError, IndexError):
            pass

    if transaction.get("repeated", False):
        symbols.append("R")

    if transaction.get("transaction_type", "").lower() == "cash":
        symbols.append("C")

    return "".join(symbols)