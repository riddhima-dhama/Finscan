FRAUD_RULES = {

    "High Value Foreign Transaction": {
        "pattern": "HF",
        "description":
            "High-value transaction from a foreign country"
    },

    "High Value Odd Hour Transaction": {
        "pattern": "HO",
        "description":
            "High-value transaction during unusual hours"
    },

    "High Value Foreign Odd Hour": {
        "pattern": "HFO",
        "description":
            "High-value foreign transaction during unusual hours"
    },

    "High Value Foreign Withdrawal": {
        "pattern": "HFW",
        "description":
            "High-value foreign cash withdrawal"
    },

    "High Value Odd Hour Withdrawal": {
        "pattern": "HOW",
        "description":
            "High-value withdrawal during unusual hours"
    },

    "Critical Fraud Pattern": {
        "pattern": "HFOW",
        "description":
            "High-value foreign transaction during unusual hours using withdrawal"
    }
}