"""
Return fraud detection engine
"""

from backend.rules.return_rules import ReturnRules
from backend.ml.inference import MLInferenceEngine

class ReturnEngine:
    """Return fraud detection engine"""

    def __init__(self, ml_engine: MLInferenceEngine = None):
        self.rules = ReturnRules()
        self.ml_engine = ml_engine
        self.rules_weight = 0.4
        self.ml_weight = 0.6

    def score(self, transaction_data: dict) -> dict:
        """Score transaction/order for return fraud risk"""
        rules_score = self.rules.score(transaction_data)

        # Get ML probability
        ml_probability = 0.15
        ml_latency_ms = 0
        ml_explanation = ""

        if self.ml_engine:
            try:
                ml_result = self.ml_engine.predict_return_fraud(transaction_data)
                if 'error' not in ml_result:
                    ml_probability = ml_result.get('probability', 0.15)
                    ml_latency_ms = ml_result.get('latency_ms', 0)
                    cached = ml_result.get('cached', False)
                    ml_explanation = f"ML inference {'(cached)' if cached else ''}: {ml_probability:.3f}"
                else:
                    ml_explanation = f"ML unavailable: {ml_result.get('error', 'unknown error')}"
            except Exception as e:
                ml_explanation = f"ML inference failed: {str(e)}"

        ml_score = ml_probability * 100
        final_score = (rules_score * self.rules_weight) + (ml_score * self.ml_weight)

        return {
            "rules_score": rules_score,
            "ml_probability": ml_probability,
            "ml_latency_ms": ml_latency_ms,
            "final_score": final_score,
            "confidence": min(0.95, 0.5 + abs(ml_probability - 0.5)),
            "explanation": f"Return fraud risk: rules={rules_score:.1f}, ml={ml_explanation}"
        }
