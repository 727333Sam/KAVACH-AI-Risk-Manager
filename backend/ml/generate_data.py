"""
Synthetic data generator for ML model training
Creates realistic transaction, chargeback, and return fraud datasets
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_fraud_data(n_samples=2000):
    """
    Generate synthetic fraud dataset with 25 features
    Target: is_fraud (0/1)
    """
    np.random.seed(42)
    random.seed(42)

    data = {
        # Transaction amount features
        'transaction_amount': np.random.exponential(scale=5000, size=n_samples),
        'amount_zscore': np.random.normal(0, 1, n_samples),

        # Velocity features
        'velocity_count_1h': np.random.poisson(2, n_samples),
        'velocity_count_24h': np.random.poisson(5, n_samples),
        'velocity_amount_24h': np.random.exponential(10000, n_samples),

        # Geolocation features
        'country_distance_km': np.random.exponential(500, n_samples),
        'country_new': np.random.binomial(1, 0.15, n_samples),
        'state_count_24h': np.random.poisson(1, n_samples),

        # Device features
        'device_new': np.random.binomial(1, 0.10, n_samples),
        'device_count': np.random.poisson(3, n_samples),
        'device_velocity_24h': np.random.poisson(2, n_samples),

        # Temporal features
        'hour_of_day': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'is_weekend': np.random.binomial(1, 0.3, n_samples),
        'is_night': np.random.binomial(1, 0.2, n_samples),

        # Customer features
        'customer_age_days': np.random.exponential(365, n_samples),
        'customer_txn_count': np.random.poisson(20, n_samples),
        'customer_total_amount': np.random.exponential(50000, n_samples),
        'customer_chargeback_rate': np.random.beta(2, 20, n_samples),

        # BIN/MCC features
        'card_issuer_risk_score': np.random.uniform(0, 1, n_samples),
        'mcc_fraud_rate': np.random.beta(2, 50, n_samples),

        # 3DS and auth features
        'auth_3ds': np.random.binomial(1, 0.6, n_samples),
        'auth_avs_match': np.random.binomial(1, 0.8, n_samples),
        'auth_cvv_match': np.random.binomial(1, 0.85, n_samples),

        # Additional risk indicators
        'email_domain_suspicious': np.random.binomial(1, 0.05, n_samples),
        'shipping_billing_mismatch': np.random.binomial(1, 0.10, n_samples),
    }

    df = pd.DataFrame(data)

    # Generate target variable with realistic fraud rate (~2%)
    fraud_probability = (
        0.02 +
        0.01 * (df['velocity_count_24h'] > 10) +
        0.015 * (df['country_new'] == 1) +
        0.02 * (df['device_new'] == 1) +
        0.01 * (df['amount_zscore'] > 2) +
        0.02 * (df['auth_3ds'] == 0) +
        0.015 * (df['shipping_billing_mismatch'] == 1) +
        np.random.normal(0, 0.01, n_samples)
    )
    fraud_probability = np.clip(fraud_probability, 0, 1)
    df['is_fraud'] = (np.random.random(n_samples) < fraud_probability).astype(int)

    return df

def generate_chargeback_data(n_samples=2000):
    """
    Generate synthetic chargeback dataset with 22 features
    Target: is_chargeback (0/1)
    """
    np.random.seed(42)
    random.seed(42)

    data = {
        # Transaction metadata
        'transaction_amount': np.random.exponential(3000, n_samples),
        'transaction_days_old': np.random.exponential(20, n_samples),
        'is_recurring': np.random.binomial(1, 0.3, n_samples),
        'mcc_code': np.random.randint(1000, 9999, n_samples),

        # Customer history
        'customer_age_days': np.random.exponential(400, n_samples),
        'customer_txn_count': np.random.poisson(15, n_samples),
        'customer_avg_txn_amount': np.random.exponential(2000, n_samples),
        'customer_lifetime_value': np.random.exponential(50000, n_samples),
        'customer_chargeback_history': np.random.poisson(1, n_samples),
        'customer_dispute_rate': np.random.beta(1, 50, n_samples),

        # Merchant features
        'merchant_category_risk': np.random.beta(2, 10, n_samples),
        'merchant_chargeback_rate': np.random.beta(1, 100, n_samples),
        'merchant_avg_txn_amount': np.random.exponential(3000, n_samples),

        # Transaction characteristics
        'card_present': np.random.binomial(1, 0.4, n_samples),
        'auth_3ds': np.random.binomial(1, 0.5, n_samples),
        'auth_avs_match': np.random.binomial(1, 0.8, n_samples),

        # Time features
        'hour_of_day': np.random.randint(0, 24, n_samples),
        'is_weekend': np.random.binomial(1, 0.3, n_samples),

        # Delivery/fulfillment
        'has_tracking': np.random.binomial(1, 0.7, n_samples),
        'delivery_days': np.random.exponential(5, n_samples),
        'refund_issued': np.random.binomial(1, 0.1, n_samples),
    }

    df = pd.DataFrame(data)

    # Generate target variable with realistic chargeback rate (~1%)
    chargeback_probability = (
        0.01 +
        0.015 * (df['customer_chargeback_history'] > 2) +
        0.02 * (df['merchant_chargeback_rate'] > 0.05) +
        0.01 * (df['auth_3ds'] == 0) +
        0.015 * (df['has_tracking'] == 0) +
        0.01 * (df['transaction_days_old'] > 30) +
        np.random.normal(0, 0.005, n_samples)
    )
    chargeback_probability = np.clip(chargeback_probability, 0, 1)
    df['is_chargeback'] = (np.random.random(n_samples) < chargeback_probability).astype(int)

    return df

def generate_return_fraud_data(n_samples=2000):
    """
    Generate synthetic return fraud dataset with 18 features
    Target: is_return_fraud (0/1)
    """
    np.random.seed(42)
    random.seed(42)

    data = {
        # Return history
        'return_count': np.random.poisson(1, n_samples),
        'return_rate': np.random.beta(1, 20, n_samples),
        'high_value_return_count': np.random.poisson(0.5, n_samples),
        'return_to_purchase_ratio': np.random.beta(1, 5, n_samples),

        # Customer patterns
        'customer_age_days': np.random.exponential(500, n_samples),
        'customer_txn_count': np.random.poisson(25, n_samples),
        'customer_lifetime_value': np.random.exponential(75000, n_samples),
        'customer_avg_txn_amount': np.random.exponential(2500, n_samples),
        'customer_return_fraud_history': np.random.binomial(1, 0.05, n_samples),

        # Item metadata
        'item_price': np.random.exponential(3000, n_samples),
        'item_category': np.random.randint(0, 20, n_samples),
        'item_return_rate': np.random.beta(2, 50, n_samples),
        'is_high_return_category': np.random.binomial(1, 0.2, n_samples),

        # Return characteristics
        'return_days_from_purchase': np.random.exponential(10, n_samples),
        'return_reason_suspicious': np.random.binomial(1, 0.1, n_samples),
        'item_condition_ok': np.random.binomial(1, 0.9, n_samples),

        # Temporal features
        'is_return_window_edge': np.random.binomial(1, 0.15, n_samples),
        'seasonal_high_return_period': np.random.binomial(1, 0.25, n_samples),
    }

    df = pd.DataFrame(data)

    # Generate target variable with realistic return fraud rate (~3%)
    return_fraud_probability = (
        0.03 +
        0.03 * (df['high_value_return_count'] > 1) +
        0.04 * (df['return_rate'] > 0.5) +
        0.05 * (df['customer_return_fraud_history'] == 1) +
        0.02 * (df['is_high_return_category'] == 1) +
        0.015 * (df['return_reason_suspicious'] == 1) +
        0.01 * (df['is_return_window_edge'] == 1) +
        np.random.normal(0, 0.01, n_samples)
    )
    return_fraud_probability = np.clip(return_fraud_probability, 0, 1)
    df['is_return_fraud'] = (np.random.random(n_samples) < return_fraud_probability).astype(int)

    return df

if __name__ == "__main__":
    # Generate all datasets
    print("Generating fraud dataset...")
    fraud_df = generate_fraud_data(2000)
    fraud_df.to_csv("/tmp/fraud_data.csv", index=False)
    print(f"Fraud data: {fraud_df.shape} - {fraud_df['is_fraud'].sum()} positive cases")

    print("Generating chargeback dataset...")
    chargeback_df = generate_chargeback_data(2000)
    chargeback_df.to_csv("/tmp/chargeback_data.csv", index=False)
    print(f"Chargeback data: {chargeback_df.shape} - {chargeback_df['is_chargeback'].sum()} positive cases")

    print("Generating return fraud dataset...")
    return_df = generate_return_fraud_data(2000)
    return_df.to_csv("/tmp/return_fraud_data.csv", index=False)
    print(f"Return fraud data: {return_df.shape} - {return_df['is_return_fraud'].sum()} positive cases")

    print("All datasets generated successfully!")
