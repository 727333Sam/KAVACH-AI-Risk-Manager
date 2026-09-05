"""
SQLAlchemy database models
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.database import Base

class Transaction(Base):
    """Transaction model"""
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    razorpay_payment_id = Column(String, unique=True, index=True)
    merchant_id = Column(String, index=True)
    customer_id = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String, default="INR")
    card_bin = Column(String, nullable=True)
    card_last4 = Column(String, nullable=True)
    category = Column(String)
    status = Column(String, default="authorized")

    # Metadata
    ip_address = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    geolocation_country = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    risk_scores = relationship("RiskScore", back_populates="transaction")
    actions = relationship("RiskAction", back_populates="transaction")

class RiskScore(Base):
    """Risk scoring results"""
    __tablename__ = "risk_scores"

    id = Column(String, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transactions.id"), index=True)

    # Fraud scores
    fraud_rules_score = Column(Float)
    fraud_ml_probability = Column(Float)
    fraud_final_score = Column(Float)
    fraud_confidence = Column(Float)

    # Chargeback scores
    chargeback_rules_score = Column(Float)
    chargeback_ml_probability = Column(Float)
    chargeback_final_score = Column(Float)
    chargeback_confidence = Column(Float)

    # Return fraud scores
    return_fraud_rules_score = Column(Float)
    return_fraud_ml_probability = Column(Float)
    return_fraud_final_score = Column(Float)
    return_fraud_confidence = Column(Float)

    # Overall
    combined_risk_score = Column(Float)
    recommended_action = Column(String)  # ALLOW, ALERT, FLAG, HOLD, BLOCK
    explanation = Column(String)

    # Engines used
    enabled_engines = Column(JSON)  # {"fraud": true, "chargeback": true, "return": false}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship
    transaction = relationship("Transaction", back_populates="risk_scores")

class RiskAction(Base):
    """Actions taken on transactions"""
    __tablename__ = "risk_actions"

    id = Column(String, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transactions.id"), index=True)

    action_type = Column(String)  # ALERT, FLAG, HOLD, EVIDENCE, BLOCK
    action_reason = Column(String)
    merchant_decision = Column(String, nullable=True)  # APPROVED, DECLINED, MANUAL_REVIEW

    # Outcomes
    actual_fraud = Column(Boolean, nullable=True)  # Ground truth (set after resolution)
    outcome = Column(String, nullable=True)  # LEGITIMATE, FRAUD_CONFIRMED, CHARGEBACK_FILED

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)

    # Relationship
    transaction = relationship("Transaction", back_populates="actions")

class MerchantConfig(Base):
    """Merchant configuration for risk engines"""
    __tablename__ = "merchant_configs"

    id = Column(String, primary_key=True, index=True)
    merchant_id = Column(String, unique=True, index=True)

    # Engine toggles
    fraud_detector_enabled = Column(Boolean, default=True)
    chargeback_predictor_enabled = Column(Boolean, default=True)
    return_fraud_classifier_enabled = Column(Boolean, default=False)

    # Action modes
    fraud_action_mode = Column(String, default="ALERT")  # ALERT, FLAG, HOLD, BLOCK
    chargeback_action_mode = Column(String, default="ALERT")
    return_action_mode = Column(String, default="ALERT")

    # Thresholds (0-1)
    fraud_threshold = Column(Float, default=0.75)
    chargeback_threshold = Column(Float, default=0.65)
    return_fraud_threshold = Column(Float, default=0.70)

    # ML/Rules ratio (rules_weight: 0-1, ml_weight: 1 - rules_weight)
    rules_weight = Column(Float, default=0.4)

    # Config JSON for advanced settings
    advanced_config = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
