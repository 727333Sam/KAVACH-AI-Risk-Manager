"""
Fraud detection rules (heuristics)
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging

logger = logging.getLogger(__name__)


class FraudRules:
    """Rule-based fraud detection using heuristic analysis"""

    def __init__(self, db: Session):
        """
        Initialize fraud rules with database session.

        Args:
            db: SQLAlchemy database session for querying transaction history
        """
        self.db = db

    def score(self, transaction_data: dict) -> float:
        """
        Score transaction for fraud using heuristic rules.
        Targets <50ms latency across all rules combined.

        Args:
            transaction_data: Dict containing transaction details (card_bin, card_last4,
                            device_id, ip_country, created_at, category, amount, customer_id)

        Returns:
            float: Risk score 0-100 (capped at 100)
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
        Rule 1: Velocity Check
        Flag if >5 transactions from same card in 10 minutes.
        Indicates potential card compromise or testing of stolen card.

        Score: +25 if 5+ transactions detected, +0 otherwise

        Args:
            txn: Transaction dict with card_bin and card_last4

        Returns:
            float: 0.0 or 25.0
        """
        try:
            from backend.db.models import Transaction

            card_bin = txn.get("card_bin")
            card_last4 = txn.get("card_last4")

            if not card_bin or not card_last4:
                return 0.0

            # Look back 10 minutes from transaction time
            txn_time = txn.get("created_at", datetime.utcnow())
            time_window_start = txn_time - timedelta(minutes=10)

            # Count transactions from same card in last 10 minutes
            recent_count = self.db.query(func.count(Transaction.id)).filter(
                and_(
                    Transaction.card_bin == card_bin,
                    Transaction.card_last4 == card_last4,
                    Transaction.created_at >= time_window_start,
                    Transaction.created_at <= txn_time,
                    Transaction.status != "declined"  # Exclude failed attempts
                )
            ).scalar() or 0

            if recent_count >= 5:
                return 25.0
            return 0.0

        except Exception as e:
            logger.error(f"Velocity check failed: {str(e)}")
            return 0.0

    def geolocation_mismatch(self, txn: dict) -> float:
        """
        Rule 2: Geolocation Mismatch
        Flag if IP country differs from billing country with high confidence.
        Indicates potential card-not-present fraud from different geography.

        Score: +20 if countries mismatch (excluding travel patterns)

        Args:
            txn: Transaction dict with ip_country, geolocation_country, customer_id

        Returns:
            float: 0.0 to 20.0
        """
        try:
            ip_country = txn.get("ip_country", "").upper()
            billing_country = txn.get("geolocation_country", "").upper()

            if not ip_country or not billing_country:
                return 0.0

            # Same country = no risk
            if ip_country == billing_country:
                return 0.0

            # Check customer's historical transaction countries
            from backend.db.models import Transaction

            customer_id = txn.get("customer_id")
            if not customer_id:
                return 20.0  # Unknown customer with geo mismatch = suspicious

            # Get customer's last 20 transactions to check if mismatch is anomalous
            last_countries = self.db.query(Transaction.geolocation_country).filter(
                Transaction.customer_id == customer_id
            ).order_by(Transaction.created_at.desc()).limit(20).all()

            customer_countries = set(c[0].upper() for c in last_countries if c[0])

            # If customer regularly transacts from this IP country, lower risk
            if ip_country in customer_countries:
                return 0.0

            # Mismatch is anomalous for this customer
            return 20.0

        except Exception as e:
            logger.error(f"Geolocation check failed: {str(e)}")
            return 0.0

    def device_fingerprint(self, txn: dict) -> float:
        """
        Rule 3: Device Fingerprint Mismatch
        Flag if transaction from device never previously used with this card.
        Indicates potential card compromise (different device).

        Score: +15 if device-card combo is new, +0 if established

        Args:
            txn: Transaction dict with device_id, card_bin, card_last4, customer_id

        Returns:
            float: 0.0 or 15.0
        """
        try:
            device_id = txn.get("device_id")
            card_bin = txn.get("card_bin")
            card_last4 = txn.get("card_last4")

            if not all([device_id, card_bin, card_last4]):
                return 0.0

            from backend.db.models import Transaction

            # Check if this device has been used with this card before
            prev_device_card_txn = self.db.query(Transaction.id).filter(
                and_(
                    Transaction.device_id == device_id,
                    Transaction.card_bin == card_bin,
                    Transaction.card_last4 == card_last4,
                    Transaction.status == "authorized"  # Only successful transactions
                )
            ).first()

            if prev_device_card_txn:
                return 0.0  # Device-card combo is established

            return 15.0  # New device-card combination

        except Exception as e:
            logger.error(f"Device fingerprint check failed: {str(e)}")
            return 0.0

    def bin_risk_check(self, txn: dict) -> float:
        """
        Rule 4: BIN Risk Check
        Flag if BIN is on known-compromised list.
        Indicates card from a batch known to have fraud incidents.

        Score: +25 if BIN is high-risk, +0 otherwise

        Args:
            txn: Transaction dict with card_bin

        Returns:
            float: 0.0 or 25.0
        """
        try:
            card_bin = txn.get("card_bin")
            if not card_bin:
                return 0.0

            # Known compromised BINs from industry databases
            # In production, this would query a dedicated BIN risk database
            compromised_bins = {
                "453456", "453457", "453458",  # Example compromised BINs
                "412345", "412346",
                "534562", "534563"
            }

            # Check first 6 digits of card
            bin_prefix = card_bin[:6] if len(card_bin) >= 6 else card_bin

            if bin_prefix in compromised_bins:
                return 25.0

            return 0.0

        except Exception as e:
            logger.error(f"BIN risk check failed: {str(e)}")
            return 0.0

    def time_of_day_anomaly(self, txn: dict) -> float:
        """
        Rule 5: Time-of-Day Anomaly
        Flag if transaction occurs at unusual hour for customer's typical pattern.
        Indicates potential account takeover (fraudster transacting at different times).

        Score: +10 if transaction hour is anomalous (outside customer's typical window)

        Args:
            txn: Transaction dict with created_at, customer_id

        Returns:
            float: 0.0 or 10.0
        """
        try:
            txn_time = txn.get("created_at", datetime.utcnow())
            customer_id = txn.get("customer_id")

            if not customer_id:
                return 0.0

            from backend.db.models import Transaction

            # Get customer's last 50 transactions to establish time pattern
            last_txns = self.db.query(Transaction.created_at).filter(
                Transaction.customer_id == customer_id
            ).order_by(Transaction.created_at.desc()).limit(50).all()

            if not last_txns:
                return 0.0  # New customer, no pattern to compare

            # Extract hours from historical transactions
            historical_hours = set(t[0].hour for t in last_txns if t[0])

            # If customer has transactions in multiple hours, be lenient
            if len(historical_hours) >= 15:  # Active across many hours
                return 0.0

            # Check if current transaction hour is within customer's pattern
            current_hour = txn_time.hour

            # Allow ±2 hour window around typical hours (account for timezones)
            hour_tolerance = set()
            for h in historical_hours:
                hour_tolerance.update([(h - 2) % 24, (h - 1) % 24, h, (h + 1) % 24, (h + 2) % 24])

            if current_hour not in hour_tolerance:
                return 10.0

            return 0.0

        except Exception as e:
            logger.error(f"Time-of-day anomaly check failed: {str(e)}")
            return 0.0

    def category_risk(self, txn: dict) -> float:
        """
        Rule 6: Category Risk
        Base score by transaction category.
        Higher-risk categories (electronics, luxury, jewelry) have higher fraud rates.

        Score: +10 for high-risk categories, +0 otherwise

        Args:
            txn: Transaction dict with category

        Returns:
            float: 0.0 or 10.0
        """
        try:
            category = txn.get("category", "").lower().strip()

            high_risk_categories = {
                "electronics", "luxury", "jewelry", "watches",
                "high_value", "gaming", "crypto"
            }

            if category in high_risk_categories:
                return 10.0

            return 0.0

        except Exception as e:
            logger.error(f"Category risk check failed: {str(e)}")
            return 0.0
