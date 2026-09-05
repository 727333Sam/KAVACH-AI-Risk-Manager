"""
Synthetic Transaction Data Generator
Creates realistic transaction data for ML model training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random
import os

fake = Faker(['en_IN', 'en_US'])  # Indian + US data for realistic names/addresses
np.random.seed(42)
random.seed(42)

class SyntheticDataGenerator:
    """Generate realistic transaction data with fraud patterns"""

    def __init__(self, n_samples=10000):
        self.n_samples = n_samples
        self.fraud_rate = 0.005  # 0.5% fraud
        self.chargeback_rate = 0.003  # 0.3% chargeback
        self.return_fraud_rate = 0.002  # 0.2% return fraud

        # Known compromised BINs for fraud simulation
        self.compromised_bins = ['453456', '453457', '412345', '534562']

        # Categories with risk profiles
        self.categories = {
            'electronics': {'avg_amount': 15000, 'fraud_rate': 0.008, 'chargeback_rate': 0.005},
            'fashion': {'avg_amount': 3000, 'fraud_rate': 0.003, 'chargeback_rate': 0.002},
            'luxury': {'avg_amount': 50000, 'fraud_rate': 0.01, 'chargeback_rate': 0.008},
            'digital_goods': {'avg_amount': 2000, 'fraud_rate': 0.006, 'chargeback_rate': 0.01},
            'groceries': {'avg_amount': 1500, 'fraud_rate': 0.001, 'chargeback_rate': 0.001},
            'jewelry': {'avg_amount': 25000, 'fraud_rate': 0.007, 'chargeback_rate': 0.006},
        }

    def generate(self) -> pd.DataFrame:
        """Generate full dataset with all features"""
        print(f"Generating {self.n_samples} synthetic transactions...")

        data = []
        base_time = datetime.now() - timedelta(days=90)

        # Generate customer pool (20% of transactions for repeat patterns)
        n_customers = int(self.n_samples * 0.2)
        customer_ids = [f"cust_{i:06d}" for i in range(n_customers)]

        for i in range(self.n_samples):
            # 80% new customers, 20% repeat
            if random.random() < 0.8:
                customer_id = f"cust_{len(customer_ids) + i:06d}"
            else:
                customer_id = random.choice(customer_ids)

            # Select category
            category = random.choices(
                list(self.categories.keys()),
                weights=[30, 25, 5, 15, 20, 5],  # Weight distribution
                k=1
            )[0]

            cat_profile = self.categories[category]

            # Generate amount (log-normal distribution)
            amount = np.random.lognormal(
                mean=np.log(cat_profile['avg_amount']),
                sigma=0.5
            )
            amount = round(max(100, min(amount, 200000)), 2)

            # Generate card details
            if random.random() < 0.01:  # 1% use compromised BINs
                card_bin = random.choice(self.compromised_bins)
            else:
                card_bin = f"{random.choice(['4', '5'])}{random.randint(10000, 99999)}"

            card_last4 = f"{random.randint(0, 9999):04d}"

            # Generate location data
            ip_country = random.choices(['IN', 'US', 'GB', 'SG', 'AE'], weights=[70, 15, 5, 5, 5])[0]
            billing_country = ip_country if random.random() < 0.95 else random.choice(['IN', 'US', 'GB'])

            # Generate device data
            device_id = fake.uuid4()

            # Generate timestamp
            timestamp = base_time + timedelta(
                days=random.randint(0, 89),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            hour_of_day = timestamp.hour
            day_of_week = timestamp.weekday()

            # Determine if transaction is fraud/chargeback/return fraud
            is_fraud = self._is_fraud(category, cat_profile, card_bin, ip_country, billing_country)
            is_chargeback = self._is_chargeback(category, cat_profile, amount) if not is_fraud else False
            is_return_fraud = self._is_return_fraud(category) if not (is_fraud or is_chargeback) else False

            # Velocity features (simulated)
            velocity_count = 1
            if is_fraud and random.random() < 0.6:  # 60% of fraud has velocity
                velocity_count = random.randint(5, 12)

            data.append({
                'transaction_id': f"txn_{i:08d}",
                'customer_id': customer_id,
                'merchant_id': f"merchant_{random.randint(1, 100):03d}",
                'amount': amount,
                'currency': 'INR',
                'category': category,
                'card_bin': card_bin,
                'card_last4': card_last4,
                'ip_country': ip_country,
                'billing_country': billing_country,
                'shipping_country': billing_country,
                'device_id': device_id,
                'hour_of_day': hour_of_day,
                'day_of_week': day_of_week,
                'velocity_count': velocity_count,
                'customer_age_days': random.randint(1, 730),
                'previous_orders': random.randint(0, 50),
                'customer_lifetime_value': round(random.uniform(0, 100000), 2),
                'previous_disputes': random.randint(0, 3),
                'return_rate': round(random.uniform(0, 0.5), 2),
                'created_at': timestamp.isoformat(),
                'is_fraud': int(is_fraud),
                'is_chargeback': int(is_chargeback),
                'is_return_fraud': int(is_return_fraud)
            })

        df = pd.DataFrame(data)
        print(f"Generated {len(df)} transactions:")
        print(f"  - Fraud: {df['is_fraud'].sum()} ({df['is_fraud'].mean()*100:.2f}%)")
        print(f"  - Chargeback: {df['is_chargeback'].sum()} ({df['is_chargeback'].mean()*100:.2f}%)")
        print(f"  - Return Fraud: {df['is_return_fraud'].sum()} ({df['is_return_fraud'].mean()*100:.2f}%)")

        return df

    def _is_fraud(self, category, cat_profile, card_bin, ip_country, billing_country) -> bool:
        """Determine if transaction should be labeled as fraud"""
        fraud_score = 0

        # Compromised BIN
        if card_bin in self.compromised_bins:
            fraud_score += 0.5

        # Geolocation mismatch
        if ip_country != billing_country:
            fraud_score += 0.3

        # Category risk
        fraud_score += cat_profile['fraud_rate']

        # Random component
        fraud_score += random.uniform(0, 0.2)

        return fraud_score > 0.7

    def _is_chargeback(self, category, cat_profile, amount) -> bool:
        """Determine if transaction should be labeled as chargeback-prone"""
        chargeback_score = 0

        # High-value items
        if amount > 20000:
            chargeback_score += 0.3

        # Category risk
        chargeback_score += cat_profile['chargeback_rate']

        # Random component
        chargeback_score += random.uniform(0, 0.2)

        return chargeback_score > 0.6

    def _is_return_fraud(self, category) -> bool:
        """Determine if transaction should be labeled as return fraud"""
        # Fashion and electronics have higher return fraud
        if category in ['fashion', 'electronics', 'luxury']:
            return random.random() < 0.005
        return random.random() < 0.001

def main():
    """Generate and save synthetic dataset"""
    # Create output directory
    os.makedirs('backend/ml/data', exist_ok=True)

    # Generate data
    generator = SyntheticDataGenerator(n_samples=10000)
    df = generator.generate()

    # Save full dataset
    output_path = 'backend/ml/data/synthetic_transactions.csv'
    df.to_csv(output_path, index=False)
    print(f"\nSaved full dataset to: {output_path}")

    # Create train/test split (80/20)
    from sklearn.model_selection import train_test_split

    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df[['is_fraud', 'is_chargeback', 'is_return_fraud']].apply(tuple, axis=1)
    )

    train_df.to_csv('backend/ml/data/train.csv', index=False)
    test_df.to_csv('backend/ml/data/test.csv', index=False)

    print(f"Created train set: {len(train_df)} samples")
    print(f"Created test set: {len(test_df)} samples")

    # Generate README
    readme_content = """# Synthetic Transaction Data

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

Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open('backend/ml/data/README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("\nDataset generation complete!")

if __name__ == '__main__':
    main()
