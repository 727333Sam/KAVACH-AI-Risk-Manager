"""
Chargeback prediction rules
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging

logger = logging.getLogger(__name__)


class ChargebackRules:
    """Rule-based chargeback risk prediction using historical patterns"""

    def __init__(self, db: Session):
        """
        Initialize chargeback rules with database session.

        Args:
            db: SQLAlchemy database session for querying transaction history
        """
        self.db = db

    def score(self, transaction_data: dict) -> float:
        """
        Score transaction for chargeback risk using heuristic rules.
        Targets <50ms latency across all rules combined.

        Args:
            transaction_data: Dict containing transaction details (customer_id, amount,
                            category, created_at, merchant_id, card_bin)

        Returns:
            float: Risk score 0-100 (capped at 100)
        """
        score = 0.0

        # Rule 1: High-value first transaction
        score += self.high_value_first_txn(transaction_data)

        # Rule 2: Quick return pattern
        score += self.quick_return_pattern(transaction_data)

        # Rule 3: No tracking interaction
        score += self.no_tracking_interaction(transaction_data)

        # Rule 4: High-risk category
        score += self.category_chargeback_risk(transaction_data)

        # Rule 5: New customer + high amount
        score += self.new_customer_high_amount(transaction_data)

        return min(score, 100.0)

    def high_value_first_txn(self, txn: dict) -> float:
        """
        Rule 1: High-Value First Transaction
        Flag if first transaction from new customer is high-value.
        Indicates potential "bust-out" fraud (make large purchase then disappear).

        Score: +20 if first txn and amount > ₹10,000, +0 otherwise

        Args:
            txn: Transaction dict with customer_id, amount, merchant_id

        Returns:
            float: 0.0 or 20.0
        """
        try:
            from backend.db.models import Transaction

            customer_id = txn.get("customer_id")
            amount = txn.get("amount", 0)
            merchant_id = txn.get("merchant_id")

            if not customer_id or not merchant_id:
                return 0.0

            # Check if this is customer's first transaction with this merchant
            prev_txn_count = self.db.query(func.count(Transaction.id)).filter(
                and_(
                    Transaction.customer_id == customer_id,
                    Transaction.merchant_id == merchant_id,
                    Transaction.status == "authorized"
                )
            ).scalar() or 0

            # First transaction + high value (₹10,000+) = suspicious
            if prev_txn_count == 0 and amount >= 10000:
                return 20.0

            return 0.0

        except Exception as e:
            logger.error(f"High-value first transaction check failed: {str(e)}")
            return 0.0

    def quick_return_pattern(self, txn: dict) -> float:
        """
        Rule 2: Quick Return Pattern
        Flag if customer has history of returning items within 48 hours.
        Indicates serial returner or "wardrobing" behavior.

        Score: +15 if customer has >2 quick returns in last 90 days, +0 otherwise

        Args:
            txn: Transaction dict with customer_id

        Returns:
            float: 0.0 or 15.0
        """
        try:
            from backend.db.models import Transaction, RiskAction

            customer_id = txn.get("customer_id")
            if not customer_id:
                return 0.0

            # Look for patterns in last 90 days
            time_window = datetime.utcnow() - timedelta(days=90)

            # Query for transactions that were returned/charged back quickly
            # This would ideally join with a returns/chargebacks table
            # For now, check RiskAction outcomes
            quick_resolutions = self.db.query(func.count(RiskAction.id)).join(
                Transaction, RiskAction.transaction_id == Transaction.id
            ).filter(
                and_(
                    Transaction.customer_id == customer_id,
                    RiskAction.outcome.in_(["CHARGEBACK_FILED", "RETURNED"]),
                    RiskAction.resolved_at <= Transaction.created_at + timedelta(hours=48),
                    RiskAction.created_at >= time_window
                )
            ).scalar() or 0

            if quick_resolutions > 2:
                return 15.0

            return 0.0

        except Exception as e:
            logger.error(f"Quick return pattern check failed: {str(e)}")
            return 0.0

    def no_tracking_interaction(self, txn: dict) -> float:
        """
        Rule 3: No Tracking Interaction
        Flag if customer never checked tracking before filing dispute.
        Indicates potential friendly fraud (claiming non-delivery without verification).

        Score: +15 if customer has history of disputes without tracking checks

        Args:
            txn: Transaction dict with customer_id

        Returns:
            float: 0.0 or 15.0
        """
        try:
            from backend.db.models import Transaction, RiskAction

            customer_id = txn.get("customer_id")
            if not customer_id:
                return 0.0

            # This would ideally query a tracking_events or customer_interactions table
            # For now, we'll check if customer has chargebacks on delivered items
            # In production, this would integrate with shipping provider APIs

            # Check for chargeback history (pattern indicator)
            chargeback_history = self.db.query(func.count(RiskAction.id)).join(
                Transaction, RiskAction.transaction_id == Transaction.id
            ).filter(
                and_(
                    Transaction.customer_id == customer_id,
                    RiskAction.outcome == "CHARGEBACK_FILED",
                    RiskAction.created_at >= datetime.utcnow() - timedelta(days=180)
                )
            ).scalar() or 0

            # Multiple chargebacks = likely no-tracking-interaction pattern
            if chargeback_history >= 2:
                return 15.0

            return 0.0

        except Exception as e:
            logger.error(f"No tracking interaction check failed: {str(e)}")
            return 0.0

    def category_chargeback_risk(self, txn: dict) -> float:
        """
        Rule 4: Category Chargeback Risk
        Base score by transaction category.
        Electronics, digital goods, and luxury items have higher chargeback rates.

        Score: +15-20 based on category risk level

        Args:
            txn: Transaction dict with category

        Returns:
            float: 0.0 to 20.0
        """
        try:
            category = txn.get("category", "").lower().strip()

            # Categories with highest chargeback rates (industry data)
            high_risk_categories = {
                "electronics": 20.0,
                "digital_goods": 20.0,
                "software": 18.0,
                "luxury": 15.0,
                "jewelry": 15.0,
                "subscriptions": 12.0
            }

            return high_risk_categories.get(category, 0.0)

        except Exception as e:
            logger.error(f"Category chargeback risk check failed: {str(e)}")
            return 0.0

    def new_customer_high_amount(self, txn: dict) -> float:
        """
        Rule 5: New Customer + High Amount
        Flag combination of new customer and high transaction amount.
        Combines customer tenure with transaction value for risk assessment.

        Score: +20 if new customer (<30 days) and amount > average by 3x, +0 otherwise

        Args:
            txn: Transaction dict with customer_id, amount, merchant_id

        Returns:
            float: 0.0 or 20.0
        """
        try:
            from backend.db.models import Transaction

            customer_id = txn.get("customer_id")
            amount = txn.get("amount", 0)
            merchant_id = txn.get("merchant_id")

            if not customer_id or not merchant_id:
                return 0.0

            # Get customer's first transaction date
            first_txn = self.db.query(Transaction.created_at).filter(
                and_(
                    Transaction.customer_id == customer_id,
                    Transaction.merchant_id == merchant_id
                )
            ).order_by(Transaction.created_at.asc()).first()

            if not first_txn:
                # New customer - check if amount is high for merchant
                merchant_avg = self._get_merchant_average_txn(merchant_id)
                if merchant_avg and amount > merchant_avg * 3:
                    return 20.0
                return 0.0

            # Check customer tenure
            customer_age_days = (datetime.utcnow() - first_txn[0]).days

            # New customer (<30 days) with high amount
            if customer_age_days < 30:
                merchant_avg = self._get_merchant_average_txn(merchant_id)
                if merchant_avg and amount > merchant_avg * 3:
                    return 20.0

            return 0.0

        except Exception as e:
            logger.error(f"New customer high amount check failed: {str(e)}")
            return 0.0

    def _get_merchant_average_txn(self, merchant_id: str) -> float:
        """
        Helper: Get average transaction amount for merchant.

        Args:
            merchant_id: Merchant identifier

        Returns:
            float: Average transaction amount or 0.0
        """
        try:
            from backend.db.models import Transaction

            # Calculate average from last 100 successful transactions
            result = self.db.query(func.avg(Transaction.amount)).filter(
                and_(
                    Transaction.merchant_id == merchant_id,
                    Transaction.status == "authorized",
                    Transaction.created_at >= datetime.utcnow() - timedelta(days=90)
                )
            ).scalar()

            return float(result) if result else 0.0

        except Exception as e:
            logger.error(f"Merchant average calculation failed: {str(e)}")
            return 0.0
