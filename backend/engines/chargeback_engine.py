"""
Chargeback prediction engine
"""

from backend.rules.chargeback_rules import ChargebackRules

class ChargebackEngine:
    """Chargeback risk prediction engine"""

    def __init__(self):
        self.rules = ChargebackRules()
        self.rules_weight = 0.4
        self.ml_weight = 0.6

    def score(self, transaction_data: dict) -> dict:
        """Score transaction for chargeback risk"""
        rules_score = self.rules.score(transaction_data)
        ml_probability = 0.2  # Placeholder for ML
        ml_score = ml_probability * 100
        final_score = (rules_score * self.rules_weight) + (ml_score * self.ml_weight)

        return {
            "rules_score": rules_score,
            "ml_probability": ml_probability,
            "final_score": final_score,
            "confidence": 0.75,
            "explanation": "Chargeback risk assessment"
        }
