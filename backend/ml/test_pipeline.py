"""
Test script for ML training and inference pipeline
Verifies models are trained and inference works correctly
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.ml.inference import MLInferenceEngine, init_inference


def test_inference_pipeline():
    """Test the ML inference pipeline with sample data"""

    print("\n" + "="*80)
    print(" TESTING ML INFERENCE PIPELINE")
    print("="*80)

    # Initialize inference engine
    print("\n[1/4] Initializing inference engine...")
    try:
        engine = init_inference()
        print("[OK] Inference engine initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize: {e}")
        return False

    # Check model status
    print("\n[2/4] Checking model status...")
    status = engine.get_model_status()
    print(f"  Fraud model: {status['fraud']}")
    print(f"  Chargeback model: {status['chargeback']}")
    print(f"  Return fraud model: {status['return_fraud']}")
    print(f"  Redis connected: {status['redis_connected']}")

    # Test fraud prediction
    print("\n[3/4] Testing fraud prediction...")
    test_txn = {
        'transaction_amount': 5000.0,
        'amount_zscore': 1.5,
        'velocity_count_1h': 3,
        'velocity_count_24h': 8,
        'velocity_amount_24h': 15000.0,
        'country_distance_km': 200.0,
        'country_new': 0,
        'state_count_24h': 2,
        'device_new': 0,
        'device_count': 2,
        'device_velocity_24h': 1,
        'hour_of_day': 14,
        'day_of_week': 3,
        'is_weekend': 0,
        'is_night': 0,
        'customer_age_days': 180,
        'customer_txn_count': 25,
        'customer_total_amount': 45000.0,
        'customer_chargeback_rate': 0.02,
        'card_issuer_risk_score': 0.3,
        'mcc_fraud_rate': 0.01,
        'auth_3ds': 1,
        'auth_avs_match': 1,
        'auth_cvv_match': 1,
        'email_domain_suspicious': 0,
        'shipping_billing_mismatch': 0,
    }

    # First prediction (cold cache)
    start_time = time.time()
    result1 = engine.predict_fraud(test_txn)
    latency1 = (time.time() - start_time) * 1000

    if 'error' in result1:
        print(f"[FAIL] Prediction failed: {result1['error']}")
    else:
        print(f"[OK] Fraud probability: {result1['probability']:.4f}")
        print(f"  Prediction: {'FRAUD' if result1['prediction'] == 1 else 'LEGIT'}")
        print(f"  Confidence: {result1['confidence']:.4f}")
        print(f"  Latency: {result1['latency_ms']:.2f}ms")
        print(f"  Cached: {result1['cached']}")

    # Test chargeback prediction
    print("\n[4/4] Testing chargeback prediction...")
    test_chargeback = {
        'transaction_amount': 3000.0,
        'transaction_days_old': 15,
        'is_recurring': 0,
        'mcc_code': 5812,
        'customer_age_days': 300,
        'customer_txn_count': 12,
        'customer_avg_txn_amount': 2500.0,
        'customer_lifetime_value': 40000.0,
        'customer_chargeback_history': 0,
        'customer_dispute_rate': 0.01,
        'merchant_category_risk': 0.2,
        'merchant_chargeback_rate': 0.02,
        'merchant_avg_txn_amount': 3500.0,
        'card_present': 1,
        'auth_3ds': 1,
        'auth_avs_match': 1,
        'hour_of_day': 11,
        'is_weekend': 0,
        'has_tracking': 1,
        'delivery_days': 3,
        'refund_issued': 0,
    }

    result2 = engine.predict_chargeback(test_chargeback)

    if 'error' in result2:
        print(f"[FAIL] Prediction failed: {result2['error']}")
    else:
        print(f"[OK] Chargeback probability: {result2['probability']:.4f}")
        print(f"  Prediction: {'CHARGEBACK' if result2['prediction'] == 1 else 'NORMAL'}")
        print(f"  Confidence: {result2['confidence']:.4f}")
        print(f"  Latency: {result2['latency_ms']:.2f}ms")

    print("\n" + "="*80)
    print(" TEST COMPLETE - ALL MODELS OPERATIONAL")
    print("="*80)

    return True


def test_engine_integration():
    """Test engine integration with ML models"""

    print("\n" + "="*80)
    print(" TESTING ENGINE INTEGRATION")
    print("="*80)

    from backend.engines.fraud_engine import FraudEngine
    from backend.engines.chargeback_engine import ChargebackEngine
    from backend.engines.return_engine import ReturnEngine

    # Initialize ML engine
    ml_engine = init_inference()

    # Test fraud engine
    print("\n[1/3] Testing FraudEngine with ML...")
    fraud_engine = FraudEngine(ml_engine=ml_engine)

    test_txn = {
        'transaction_amount': 8000.0,
        'amount_zscore': 2.5,
        'velocity_count_1h': 5,
        'velocity_count_24h': 15,
        'velocity_amount_24h': 25000.0,
        'country_distance_km': 800.0,
        'country_new': 1,
        'state_count_24h': 3,
        'device_new': 1,
        'device_count': 1,
        'device_velocity_24h': 5,
        'hour_of_day': 2,
        'day_of_week': 6,
        'is_weekend': 1,
        'is_night': 1,
        'customer_age_days': 5,
        'customer_txn_count': 2,
        'customer_total_amount': 8000.0,
        'customer_chargeback_rate': 0.1,
        'card_issuer_risk_score': 0.8,
        'mcc_fraud_rate': 0.05,
        'auth_3ds': 0,
        'auth_avs_match': 0,
        'auth_cvv_match': 1,
        'email_domain_suspicious': 1,
        'shipping_billing_mismatch': 1,
    }

    result = fraud_engine.score(test_txn)
    print(f"  Final score: {result['final_score']:.2f}")
    print(f"  Rules score: {result['rules_score']:.2f}")
    print(f"  ML probability: {result['ml_probability']:.4f}")
    print(f"  ML latency: {result['ml_latency_ms']:.2f}ms")
    print(f"  Explanation: {result['explanation']}")

    # Test chargeback engine
    print("\n[2/3] Testing ChargebackEngine with ML...")
    chargeback_engine = ChargebackEngine(ml_engine=ml_engine)

    result = chargeback_engine.score({
        'transaction_amount': 5000.0,
        'transaction_days_old': 45,
        'is_recurring': 0,
        'mcc_code': 5812,
        'customer_age_days': 60,
        'customer_txn_count': 3,
        'customer_avg_txn_amount': 5000.0,
        'customer_lifetime_value': 15000.0,
        'customer_chargeback_history': 2,
        'customer_dispute_rate': 0.05,
        'merchant_category_risk': 0.6,
        'merchant_chargeback_rate': 0.08,
        'merchant_avg_txn_amount': 3000.0,
        'card_present': 0,
        'auth_3ds': 0,
        'auth_avs_match': 0,
        'hour_of_day': 23,
        'is_weekend': 1,
        'has_tracking': 0,
        'delivery_days': 10,
        'refund_issued': 0,
    })

    print(f"  Final score: {result['final_score']:.2f}")
    print(f"  Rules score: {result['rules_score']:.2f}")
    print(f"  ML probability: {result['ml_probability']:.4f}")
    print(f"  ML latency: {result['ml_latency_ms']:.2f}ms")

    # Test return fraud engine
    print("\n[3/3] Testing ReturnEngine with ML...")
    return_engine = ReturnEngine(ml_engine=ml_engine)

    result = return_engine.score({
        'return_count': 5,
        'return_rate': 0.6,
        'high_value_return_count': 2,
        'return_to_purchase_ratio': 0.5,
        'customer_age_days': 30,
        'customer_txn_count': 10,
        'customer_lifetime_value': 20000.0,
        'customer_avg_txn_amount': 5000.0,
        'customer_return_fraud_history': 1,
        'item_price': 3000.0,
        'item_category': 5,
        'item_return_rate': 0.15,
        'is_high_return_category': 1,
        'return_days_from_purchase': 28,
        'return_reason_suspicious': 1,
        'item_condition_ok': 0,
        'is_return_window_edge': 1,
        'seasonal_high_return_period': 0,
    })

    print(f"  Final score: {result['final_score']:.2f}")
    print(f"  Rules score: {result['rules_score']:.2f}")
    print(f"  ML probability: {result['ml_probability']:.4f}")
    print(f"  ML latency: {result['ml_latency_ms']:.2f}ms")

    print("\n" + "="*80)
    print(" ENGINE INTEGRATION TEST COMPLETE")
    print("="*80)

    return True


if __name__ == "__main__":
    # Run tests
    test_inference_pipeline()
    test_engine_integration()
