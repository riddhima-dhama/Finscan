FRAUD_RULES = {

    "High Value Foreign Transaction": {
        "pattern": "HF",
        "description": "High-value transaction from a foreign country"
    },

    "High Value Odd Hour Transaction": {
        "pattern": "HO",
        "description": "High-value transaction during unusual hours"
    },

    "Repeated High Value Pattern": {
        "pattern": "(HR)+",
        "description": "One or more repeated high-value transaction patterns"
    },

    "Foreign or Odd Hour High Value Transaction": {
        "pattern": "H(F|O)",
        "description": "High-value transaction involving either a foreign location or unusual hour"
    },

    "Critical Fraud Pattern": {
        "pattern": "HFOR",
        "description": "High-value foreign transaction at an unusual hour with repeated activity"
    }
}