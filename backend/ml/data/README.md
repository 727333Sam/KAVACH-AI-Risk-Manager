# Synthetic Transaction Data

## Dataset Overview
- **Total Transactions**: 10,000
- **Fraud Rate**: ~0.5% (50 transactions)
- **Chargeback Rate**: ~0.3% (30 transactions)
- **Return Fraud Rate**: ~0.2% (20 transactions)

## Features (25 total)
1. Transaction metadata: amount, category, currency, card_bin, card_last4
2. Customer data: customer_id, customer_age_days, customer_lifetime_value, previous_orders
3. Geolocation: ip_country, billing_country, shipping_country
4. Device: device_id
5. Temporal: hour_of_day, day_of_week, created_at
6. History: velocity_count, previous_disputes, return_rate
7. Labels: is_fraud, is_chargeback, is_return_fraud

## Fraud Patterns Simulated
- **Velocity attacks**: Same card, 5+ transactions in short time
- **Compromised BINs**: Known high-risk card prefixes
- **Geolocation mismatches**: IP country ≠ billing country
- **Category risk**: Electronics, luxury, digital goods

## Files
- `synthetic_transactions.csv` — Full dataset
- `train.csv` — 80% for training (8,000 samples)
- `test.csv` — 20% for testing (2,000 samples)

## Usage
```python
import pandas as pd

# Load training data
train_df = pd.read_csv('backend/ml/data/train.csv')

# Separate features and labels
X_train = train_df.drop(['is_fraud', 'is_chargeback', 'is_return_fraud'], axis=1)
y_fraud = train_df['is_fraud']
y_chargeback = train_df['is_chargeback']
y_return = train_df['is_return_fraud']
```

Generated: 2026-09-05 08:52:29