"""
Return fraud detection rules
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging

logger = logging.getLogger(__name__)


class ReturnRules:
    """Rule-based return fraud detection using historical patterns"""

    def __init__(self, db: Session):
        """
        Initialize return fraud rules with database session.

        Args:
            db: SQLAlchemy database session for querying transaction history
        """
        self.db = db

    def score(self, transaction_data: dict) -> float:
        """
        Score transaction for return fraud risk using heuristic rules.
        Targets <50ms latency across all rules combined.

        Args:
            transaction_data: Dict containing transaction details (customer_id, amount,
                            category, merchant_id, card_bin)

        Returns:
            float: Risk score 0-100 (capped at 100)
        """
        score = 0.0

        # Rule 1: Wardrobing pattern (return rate > 40%)
        score += self.wardrobing_pattern(transaction_data)

        # Rule 2: Serial returner (>5 returns in 30 days)
        score += self.serial_returner(transaction_data)

        # Rule 3: Counterfeit receipt (digital goods/non-returnable)
        score += self.counterfeit_receipt(transaction_data)

        # Rule 4: High-value returns (luxury/electronics frequently returned)
        score += self.high_value_returns(transaction_data)

        return min(score, 100.0)

    def wardrobing_pattern(self, txn: dict) -> float:
        """
        Rule 1: Wardrobing Pattern
        Flag if customer has return rate >40% (buying, using, returning).
        Common in fashion, electronics where items are "rented" then returned.

        Score: +25 if return rate >40%, +0 otherwise

        Args:
            txn: Transaction dict with customer_id, merchant_id

        Returns:
            float: 0.0 or 25.0
        """
        try:
            from backend.db.models import Transaction, RiskAction

            customer_id = txn.get("customer_id")
            merchant_id = txn.get("merchant_id")

            if not customer_id or not merchant_id:
                return 0.0

            # Look at customer's last 180 days of transactions
            time_window = datetime.utcnow() - timedelta(days=180)

            # Get total transactions
            total_txns = self.db.query(func.count(Transaction.id)).filter(
                and_(
                    Transaction.customer_id == customer_id,
                    Transaction.merchant_id == merchant_id,
                    Transaction.status == "authorized",
                    Transaction.created_at >= time_window
                )
            ).scalar() or 0

            if total_txns < 3:  # Need minimum history
                return 0.0

            # Get returned transactions (via RiskAction outcomes)
            returned_count = self.db.query(func.count(RiskAction.id)).join(
                Transaction, RiskAction.transaction_id == Transaction.id
            ).filter(
                and_(
                    Transaction.customer_id == customer_id,
                    Transaction.merchant_id == merchant_id,
                    RiskAction.outcome == "RETURNED",
                    RiskAction.created_at >= time_window
                )
            ).scalar() or 0

            return_rate = returned_count / total_txns if total_txns > 0 else 0.0

            if return_rate > 0.40:  # >40% return rate
                return 25.0

            return 0.0

        except Exception as e:
            logger.error(f"Wardrobing pattern check failed: {str(e)}")
            return 0.0

    def serial_returner(self, txn: dict) -> float:
        """
        Rule 2: Serial Returner
        Flag if customer has >5 returns in last 30 days.
        Indicates systematic return abuse.

        Score: +25 if >5 returns in 30 days, +0 otherwise

        Args:
            txn: Transaction dict with customer_id, merchant_id

        Returns:
            float: 0.0 or 25.0
        """
        try:
            from backend.db.models import Transaction, RiskAction

            customer_id = txn.get("customer_id")
            merchant_id = txn.get("merchant_id")

            if not customer_id or not merchant_id:
                return 0.0

            # Look at last 30 days
            time_window = datetime.utcnow() - timedelta(days=30)

            # Count returns in window
            return_count = self.db.query(func.count(RiskAction.id)).join(
                Transaction, RiskAction.transaction_id == Transaction.id
            ).filter(
                and_(
                    Transaction.customer_id == customer_id,
                    Transaction.merchant_id == merchant_id,
                    RiskAction.outcome == "RETURNED",
                    RiskAction.created_at >= time_window
                )
            ).scalar() or 0

            if return_count > 5:
                return 25.0

            return 0.0

        except Exception as e:
            logger.error(f"Serial returner check failed: {str(e)}")
            return 0.0

    def counterfeit_receipt(self, txn: dict) -> float:
        """
        Rule 3: Counterfeit Receipt
        Flag digital goods or non-returnable categories attempting returns.
        These categories have higher receipt fraud rates.

        Score: +20 if category is digital/non-returnable, +0 otherwise

        Args:
            txn: Transaction dict with category

        Returns:
            float: 0.0 or 20.0
        """
        try:
            category = txn.get("category", "").lower().strip()

            # Digital goods and non-returnable items are high-risk for receipt fraud
            digital_non_returnable = {
                "digital_goods": 20.0,
                "software": 20.0,
                "gift_cards": 25.0,
                "downloads": 20.0,
                "subscriptions": 15.0,
                "services": 15.0,
                "ebooks": 20.0,
                "music": 20.0,
                "video": 20.0
            }

            return digital_non_returnable.get(category, 0.0)

        except Exception as e:
            logger.error(f"Counterfeit receipt check failed: {str(e)}")
            return 0.0

    def high_value_returns(self, txn: dict) -> float:
        """
        Rule 4: High-Value Returns
        Flag if customer has history of returning high-value items frequently.
        Luxury and electronics are commonly "used" then returned.

        Score: +20 if customer has >2 high-value returns in last 90 days

        Args:
            txn: Transaction dict with customer_id, merchant_id, amount, category

        Returns:
            float: 0.0 or 20.0
        """
        try:
            from backend.db.models import Transaction, RiskAction

            customer_id = txn.get("customer_id")
            merchant_id = txn.get("merchant_id")
            category = txn.get("category", "").lower().strip()

            if not customer_id or not merchant_id:
                return 0.0

            # Define high-value categories
            high_value_categories = {
                "electronics", "luxury", "jewelry", "watches",
                "designer", "high_value", "appliances"
            }

            is_high_value_category = category in high_value_categories
            amount = txn.get("amount", 0)

            # Consider it high-value if category OR amount > ₹15,000
            is_high_value = is_high_value_category or amount >= 15000

            if not is_high_value:
                return 0.0

            # Look at last 90 days for high-value returns
            time_window = datetime.utcnow() - timedelta(days=90)

            # Join transactions with their values/categories to find high-value returns
            high_value_return_count = self.db.query(func.count(RiskAction.id)).join(
                Transaction, RiskAction.transaction_id == Transaction.id
            ).filter(
                and_(
                    Transaction.customer_id == customer_id,
                    Transaction.merchant_id == merchant_id,
                    RiskAction.outcome == "RETURNED",
                    RiskAction.created_at >= time_window,
                    # Either high-value category OR high amount
                    (
                        Transaction.category.in_(high_value_categories) |
                        (Transaction.amount >= 15000)
                    )
                )
            ).scalar() or 0

            if high_value_return_count > 2:
                return 20.0

            return 0.0

        except Exception as e:
            logger.error(f"High-value returns check failed: {str(e)}")
            return 0.0
