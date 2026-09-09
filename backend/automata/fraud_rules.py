FRAUD_RULES = {
    "High Value Foreign Transaction": {
        "pattern": "HF",
        "description": "High-value transaction from a foreign country"
    },

    "High Value Odd Hour Transaction": {
        "pattern": "HO",
        "description": "High-value transaction during unusual hours"
    },

    "Repeated High Value Transaction": {
        "pattern": "HRH",
        "description": "Multiple high-value transactions occurring repeatedly"
    },

    "Foreign Odd Hour Transaction": {
        "pattern": "FO",
        "description": "Foreign transaction during unusual hours"
    },

    "Critical Fraud Pattern": {
        "pattern": "HFOR",
        "description": "High-value foreign transaction at an unusual hour with repeated activity"
    }
}