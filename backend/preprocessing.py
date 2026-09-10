def convert_transaction_to_symbol(transaction):
    symbols = []

    # --------------------------------
    # AMOUNT
    # --------------------------------

    amount = float(transaction.get("amount", 0))

    if amount > 50000:
        symbols.append("H")

    elif amount >= 10000:
        symbols.append("M")

    else:
        symbols.append("L")


    # --------------------------------
    # LOCATION
    # --------------------------------

    country = str(
        transaction.get(
            "country",
            transaction.get("location", "India")
        )
    ).strip().lower()

    if country in [
        "foreign",
        "usa",
        "us",
        "uk",
        "canada",
        "australia",
        "singapore",
        "dubai"
    ]:
        symbols.append("F")

    else:
        symbols.append("D")


    # --------------------------------
    # TIME
    # --------------------------------

    time_value = transaction.get("time", "")

    try:
        hour = int(
            str(time_value).split(":")[0]
        )

        if 0 <= hour < 5:
            symbols.append("O")

        else:
            symbols.append("N")

    except (ValueError, IndexError):
        symbols.append("N")


    # --------------------------------
    # TRANSACTION TYPE
    # --------------------------------

    transaction_type = str(
        transaction.get(
            "transaction_type",
            transaction.get("type", "")
        )
    ).strip().lower()

    if transaction_type in [
        "cash",
        "withdrawal",
        "atm"
    ]:
        symbols.append("W")

    else:
        symbols.append("P")


    return "".join(symbols)


def preprocess_transactions(transactions):

    result = []

    for transaction in transactions:

        item = transaction.copy()

        item["symbol"] = convert_transaction_to_symbol(
            transaction
        )

        result.append(item)

    return result