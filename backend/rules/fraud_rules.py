"""
Fraud detection rules (heuristics)
"""

class FraudRules:
    """Rule-based fraud detection"""

    def score(self, transaction_data: dict) -> float:
        """
        Score transaction for fraud using heuristic rules
        Returns score 0-100
        """
        score = 0.0

        # Rule 1: Velocity check (5+ txns from same card in 10 mins)
        score += self.velocity_check(transaction_data)

        # Rule 2: Geolocation mismatch
        score += self.geolocation_mismatch(transaction_data)

        # Rule 3: Device fingerprint mismatch
        score += self.device_fingerprint(transaction_data)

        # Rule 4: Known compromised BIN
        score += self.bin_risk_check(transaction_data)

        # Rule 5: Time-of-day anomaly
        score += self.time_of_day_anomaly(transaction_data)

        # Rule 6: High-risk category
        score += self.category_risk(transaction_data)

        return min(score, 100.0)  # Cap at 100

    def velocity_check(self, txn: dict) -> float:
        """
        Flag if >5 transactions from same card in 10 minutes
        Score: +25 if triggered
        """
        # TODO: Query database for recent transactions
        return 0.0

    def geolocation_mismatch(self, txn: dict) -> float:
        """
        Flag if IP country ≠ billing country AND shipping far from both
        Score: +20 if triggered
        """
        # TODO: Implement geolocation logic
        return 0.0

    def device_fingerprint(self, txn: dict) -> float:
        """
        Flag if transaction from device never seen with this card
        Score: +15 if triggered
        """
        # TODO: Implement device tracking
        return 0.0

    def bin_risk_check(self, txn: dict) -> float:
        """
        Flag if BIN is on known-compromised list
        Score: +25 if triggered
        """
        # TODO: Check against BIN database
        return 0.0

    def time_of_day_anomaly(self, txn: dict) -> float:
        """
        Flag if transaction at unusual time for customer
        Score: +10 if triggered
        """
        # TODO: Implement time anomaly detection
        return 0.0

    def category_risk(self, txn: dict) -> float:
        """
        Base score by transaction category
        High-risk: +10 (electronics, luxury)
        """
        category = txn.get("category", "").lower()
        high_risk_categories = ["electronics", "luxury", "jewelry", "watches"]
        return 10.0 if category in high_risk_categories else 0.0
