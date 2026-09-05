"""
Fraud detection engine with rules + ML
"""

from backend.rules.fraud_rules import FraudRules

class FraudEngine:
    """Fraud scoring engine"""

    def __init__(self):
        self.rules = FraudRules()
        self.rules_weight = 0.4
        self.ml_weight = 0.6

    def score(self, transaction_data: dict) -> dict:
        """
        Score transaction for fraud risk

        Returns:
        {
            "rules_score": 0-100,
            "ml_probability": 0-1,
            "final_score": 0-100,
            "confidence": 0-1,
            "explanation": "string"
        }
        """
        # Get rules score
        rules_score = self.rules.score(transaction_data)

        # Get ML probability (placeholder)
        ml_probability = 0.3  # Will implement ML inference

        # Hybrid scoring: 40% rules + 60% ML
        # Convert ML probability (0-1) to 0-100 scale
        ml_score = ml_probability * 100
        final_score = (rules_score * self.rules_weight) + (ml_score * self.ml_weight)

        return {
            "rules_score": rules_score,
            "ml_probability": ml_probability,
            "final_score": final_score,
            "confidence": 0.85,
            "explanation": f"Fraud risk detected via rule scoring and ML analysis"
        }
