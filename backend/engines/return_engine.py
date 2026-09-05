"""
Return fraud detection engine
"""

from backend.rules.return_rules import ReturnRules

class ReturnEngine:
    """Return fraud detection engine"""

    def __init__(self):
        self.rules = ReturnRules()
        self.rules_weight = 0.4
        self.ml_weight = 0.6

    def score(self, transaction_data: dict) -> dict:
        """Score transaction/order for return fraud risk"""
        rules_score = self.rules.score(transaction_data)
        ml_probability = 0.15  # Placeholder for ML
        ml_score = ml_probability * 100
        final_score = (rules_score * self.rules_weight) + (ml_score * self.ml_weight)

        return {
            "rules_score": rules_score,
            "ml_probability": ml_probability,
            "final_score": final_score,
            "confidence": 0.70,
            "explanation": "Return fraud risk assessment"
        }
