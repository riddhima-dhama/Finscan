from automata.regex_to_nfa import regex_to_nfa
from automata.nfa_to_dfa import nfa_to_dfa
from automata.fraud_rules import FRAUD_RULES


def get_transaction_symbol(transaction):
    """
    Get the already-generated transaction symbol.

    Example:
        HF
        HFOC
        LDP
        M
    """

    symbol = transaction.get("symbol")

    if symbol:
        return str(symbol).strip().upper()

    # Fallback for transactions that do not already
    # contain a symbol.
    symbols = []

    amount = transaction.get("amount", 0)

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        amount = 0

    if amount > 50000:
        symbols.append("H")
    elif amount >= 10000:
        symbols.append("M")
    else:
        symbols.append("L")

    country = str(
        transaction.get(
            "country",
            transaction.get("location", "India")
        )
    )

    if country.lower() != "india":
        symbols.append("F")

    time_value = transaction.get("time")

    if time_value:
        try:
            hour = int(str(time_value).split(":")[0])

            if 0 <= hour < 5:
                symbols.append("O")

        except (ValueError, IndexError):
            pass

    transaction_type = str(
        transaction.get(
            "transaction_type",
            transaction.get("type", "")
        )
    ).lower()

    if transaction_type == "cash":
        symbols.append("C")

    if transaction.get("repeated", False):
        symbols.append("R")

    return "".join(symbols)


def simulate_dfa(dfa, input_string):
    """
    Run the complete DFA on the input string.

    Returns:
        accepted
        final_state
        path
        steps
    """

    current_state = dfa["start_state"]

    path = [f"D{current_state}"]
    steps = []

    transitions = dfa["transitions"]
    alphabet = dfa["alphabet"]

    for symbol in input_string:

        # If symbol does not belong to the DFA alphabet,
        # the input cannot be accepted.
        if symbol not in alphabet:

            steps.append({
                "symbol": symbol,
                "from_state": current_state,
                "to_state": None,
                "valid": False
            })

            path.append("DEAD")

            return {
                "accepted": False,
                "final_state": current_state,
                "path": path,
                "steps": steps
            }

        next_state = transitions.get(
            current_state,
            {}
        ).get(symbol)

        if next_state is None:

            steps.append({
                "symbol": symbol,
                "from_state": current_state,
                "to_state": None,
                "valid": False
            })

            path.append("DEAD")

            return {
                "accepted": False,
                "final_state": current_state,
                "path": path,
                "steps": steps
            }

        steps.append({
            "symbol": symbol,
            "from_state": current_state,
            "to_state": next_state,
            "valid": True
        })

        current_state = next_state

        path.append(f"D{current_state}")

    accepted = current_state in dfa["accept_states"]

    return {
        "accepted": accepted,
        "final_state": current_state,
        "path": path,
        "steps": steps
    }


def format_path(simulation):
    """
    Convert simulation steps into readable DFA path.

    Example:
        D0 --H--> D1 --F--> D2
    """

    if not simulation["steps"]:
        return f"D{simulation['final_state']}"

    output = []

    first_state = simulation["steps"][0]["from_state"]

    output.append(f"D{first_state}")

    for step in simulation["steps"]:

        symbol = step["symbol"]

        if step["to_state"] is None:
            output.append(f"--{symbol}--> DEAD")
        else:
            output.append(
                f"--{symbol}--> D{step['to_state']}"
            )

    return " ".join(output)


def build_rule_dfa(pattern):
    """
    Convert:

        Regular Expression
            ↓
        Thompson NFA
            ↓
        Subset Construction
            ↓
        DFA
    """

    nfa = regex_to_nfa(pattern)

    dfa = nfa_to_dfa(nfa)

    return dfa


def detect_fraud(transaction):
    """
    Main FinScan fraud detection function.

    Each transaction is converted into a finite symbol string.

    Every fraud rule is converted:

        Regex → NFA → DFA

    The DFA then processes the transaction symbols.

    If the final state is accepting,
    the rule is matched.
    """

    symbol_string = get_transaction_symbol(transaction)

    matched_rules = []
    execution_trace = []

    for rule_name, rule_data in FRAUD_RULES.items():

        pattern = rule_data["pattern"]

        description = rule_data.get(
            "description",
            ""
        )

        try:

            # ---------------------------------
            # REGEX → NFA → DFA
            # ---------------------------------

            dfa = build_rule_dfa(pattern)

            # ---------------------------------
            # RUN DFA
            # ---------------------------------

            simulation = simulate_dfa(
                dfa,
                symbol_string
            )

            path = format_path(simulation)

            accepted = simulation["accepted"]

            # ---------------------------------
            # EXECUTION TRACE
            # ---------------------------------

            execution_trace.append({

                "rule": rule_name,

                "pattern": pattern,

                "description": description,

                "input_symbol": symbol_string,

                "path": path,

                "final_state": simulation[
                    "final_state"
                ],

                "accepted": accepted,

                "result": (
                    "FRAUD / ACCEPT"
                    if accepted
                    else "NORMAL / REJECT"
                ),

                "steps": simulation["steps"]
            })

            # ---------------------------------
            # MATCHED RULE
            # ---------------------------------

            if accepted:

                matched_rules.append({

                    "rule": rule_name,

                    "pattern": pattern,

                    "description": description,

                    "path": path,

                    "final_state": simulation[
                        "final_state"
                    ],

                    "result": "FRAUD / ACCEPT"
                })

        except Exception as error:

            print(
                f"Error processing rule "
                f"{rule_name}: {error}"
            )

            execution_trace.append({

                "rule": rule_name,

                "pattern": pattern,

                "description": description,

                "input_symbol": symbol_string,

                "path": "ERROR",

                "final_state": None,

                "accepted": False,

                "result": "ERROR",

                "steps": [],

                "error": str(error)
            })

    return {

        "symbols": symbol_string,

        "is_fraud": len(matched_rules) > 0,

        "matched_rules": matched_rules,

        "execution_trace": execution_trace
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    test_transactions = [

        {
            "id": 1,
            "amount": 5000,
            "country": "India",
            "time": "14:30",
            "transaction_type": "online",
            "symbol": "L"
        },

        {
            "id": 2,
            "amount": 60000,
            "country": "India",
            "time": "14:30",
            "transaction_type": "online",
            "symbol": "H"
        },

        {
            "id": 3,
            "amount": 60000,
            "country": "Foreign",
            "time": "14:30",
            "transaction_type": "online",
            "symbol": "HF"
        },

        {
            "id": 4,
            "amount": 60000,
            "country": "Foreign",
            "time": "02:30",
            "transaction_type": "cash",
            "symbol": "HFOC"
        }
    ]

    print()
    print("=" * 70)
    print("FINSCAN FRAUD ENGINE TEST")
    print("=" * 70)

    for transaction in test_transactions:

        print()
        print(
            f"Transaction {transaction['id']}"
        )

        result = detect_fraud(transaction)

        print(
            "Input Symbol :",
            result["symbols"]
        )

        print(
            "Fraud        :",
            result["is_fraud"]
        )

        print()
        print("Matched Rules:")

        if result["matched_rules"]:

            for rule in result["matched_rules"]:

                print(
                    f"  - {rule['rule']}"
                )

                print(
                    f"    Pattern : "
                    f"{rule['pattern']}"
                )

                print(
                    f"    Path    : "
                    f"{rule['path']}"
                )

        else:

            print("  None")

        print()
        print("Execution Trace:")

        for trace in result["execution_trace"]:

            print()
            print(
                f"Rule   : {trace['rule']}"
            )

            print(
                f"Pattern: {trace['pattern']}"
            )

            print(
                f"Input  : {trace['input_symbol']}"
            )

            print(
                f"Path   : {trace['path']}"
            )

            print(
                f"Final  : D{trace['final_state']}"
                if trace["final_state"] is not None
                else "Final  : None"
            )

            print(
                f"Result : {trace['result']}"
            )

    print()
    print("=" * 70)