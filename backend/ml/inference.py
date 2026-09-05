"""
Fast Inference Pipeline with Redis Caching
Provides cached inference for fraud, chargeback, and return fraud models
"""

import json
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import hashlib
import time

try:
    import redis
except ImportError:
    redis = None


class MLInferenceEngine:
    """
    ML-based inference with Redis caching
    Handles feature extraction, model prediction, and caching
    """

    def __init__(self, models_dir: str = None, redis_client = None, cache_ttl: int = 3600):
        """
        Initialize inference engine

        Args:
            models_dir: Directory containing trained models
            redis_client: Redis client instance (optional)
            cache_ttl: Cache time-to-live in seconds (default 1 hour)
        """
        self.models_dir = Path(models_dir or "backend/ml/models")
        self.redis = redis_client
        self.cache_ttl = cache_ttl
        self.models = {}
        self.scalers = {}

        # Load all models and scalers on initialization
        self._load_models()

    def _load_models(self):
        """Load all trained models and scalers from disk"""
        try:
            # Fraud model
            fraud_model_path = self.models_dir / "fraud_xgboost.joblib"
            if fraud_model_path.exists():
                self.models['fraud'] = joblib.load(fraud_model_path)
                self.scalers['fraud'] = joblib.load(self.models_dir / "scalers" / "fraud_scaler.joblib")
                print(f"[OK] Loaded fraud model from {fraud_model_path}")

            # Chargeback model
            chargeback_model_path = self.models_dir / "chargeback_rf.joblib"
            if chargeback_model_path.exists():
                self.models['chargeback'] = joblib.load(chargeback_model_path)
                self.scalers['chargeback'] = joblib.load(self.models_dir / "scalers" / "chargeback_scaler.joblib")
                print(f"[OK] Loaded chargeback model from {chargeback_model_path}")

            # Return fraud model
            return_model_path = self.models_dir / "return_fraud_lr.joblib"
            if return_model_path.exists():
                self.models['return_fraud'] = joblib.load(return_model_path)
                self.scalers['return_fraud'] = joblib.load(self.models_dir / "scalers" / "return_fraud_scaler.joblib")
                print(f"[OK] Loaded return fraud model from {return_model_path}")

        except Exception as e:
            print(f"Error loading models: {e}")
            print("Models not yet trained. Run train.py to generate models.")

    def _get_cache_key(self, model_type: str, data_hash: str) -> str:
        """Generate Redis cache key"""
        return f"ml_inference:{model_type}:{data_hash}"

    def _hash_data(self, data: Dict) -> str:
        """Create hash of input data for cache key"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get prediction from Redis cache"""
        if not self.redis:
            return None

        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"Cache read error: {e}")

        return None

    def _set_to_cache(self, cache_key: str, result: Dict):
        """Store prediction in Redis cache"""
        if not self.redis:
            return

        try:
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result, default=str)
            )
        except Exception as e:
            print(f"Cache write error: {e}")

    def predict_fraud(self, transaction_data: Dict) -> Dict:
        """
        Predict fraud probability for a transaction

        Args:
            transaction_data: Dict with transaction features

        Returns:
            {
                'probability': float (0-1),
                'prediction': int (0/1),
                'confidence': float,
                'cached': bool,
                'latency_ms': float
            }
        """
        start_time = time.time()

        if 'fraud' not in self.models:
            return self._error_response("Fraud model not loaded")

        # Check cache
        data_hash = self._hash_data(transaction_data)
        cache_key = self._get_cache_key('fraud', data_hash)
        cached_result = self._get_from_cache(cache_key)

        if cached_result:
            cached_result['latency_ms'] = (time.time() - start_time) * 1000
            cached_result['cached'] = True
            return cached_result

        # Extract features
        features = self._extract_fraud_features(transaction_data)
        if features is None:
            return self._error_response("Failed to extract fraud features")

        # Scale features
        features_scaled = self.scalers['fraud'].transform([features])[0]

        # Predict
        try:
            model = self.models['fraud']
            probability = float(model.predict_proba([features_scaled])[0][1])

            # Use optimal threshold from training
            threshold = 0.45  # This should be loaded from model metadata
            prediction = int(probability >= threshold)

            result = {
                'probability': probability,
                'prediction': prediction,
                'confidence': abs(probability - 0.5) * 2,  # Higher confidence if far from threshold
                'cached': False,
                'latency_ms': (time.time() - start_time) * 1000,
                'model_version': 'xgboost_v1',
                'threshold': threshold
            }

            # Cache the result
            self._set_to_cache(cache_key, result)

            return result

        except Exception as e:
            return self._error_response(f"Fraud prediction error: {e}")

    def predict_chargeback(self, transaction_data: Dict) -> Dict:
        """
        Predict chargeback probability for a transaction

        Args:
            transaction_data: Dict with transaction features

        Returns:
            {
                'probability': float (0-1),
                'prediction': int (0/1),
                'confidence': float,
                'cached': bool,
                'latency_ms': float
            }
        """
        start_time = time.time()

        if 'chargeback' not in self.models:
            return self._error_response("Chargeback model not loaded")

        # Check cache
        data_hash = self._hash_data(transaction_data)
        cache_key = self._get_cache_key('chargeback', data_hash)
        cached_result = self._get_from_cache(cache_key)

        if cached_result:
            cached_result['latency_ms'] = (time.time() - start_time) * 1000
            cached_result['cached'] = True
            return cached_result

        # Extract features
        features = self._extract_chargeback_features(transaction_data)
        if features is None:
            return self._error_response("Failed to extract chargeback features")

        # Scale features
        features_scaled = self.scalers['chargeback'].transform([features])[0]

        # Predict
        try:
            model = self.models['chargeback']
            probability = float(model.predict_proba([features_scaled])[0][1])

            # Use optimal threshold from training
            threshold = 0.55  # This should be loaded from model metadata
            prediction = int(probability >= threshold)

            result = {
                'probability': probability,
                'prediction': prediction,
                'confidence': abs(probability - 0.5) * 2,
                'cached': False,
                'latency_ms': (time.time() - start_time) * 1000,
                'model_version': 'rf_v1',
                'threshold': threshold
            }

            # Cache the result
            self._set_to_cache(cache_key, result)

            return result

        except Exception as e:
            return self._error_response(f"Chargeback prediction error: {e}")

    def predict_return_fraud(self, transaction_data: Dict) -> Dict:
        """
        Predict return fraud probability for a return/order

        Args:
            transaction_data: Dict with return/order features

        Returns:
            {
                'probability': float (0-1),
                'prediction': int (0/1),
                'confidence': float,
                'cached': bool,
                'latency_ms': float
            }
        """
        start_time = time.time()

        if 'return_fraud' not in self.models:
            return self._error_response("Return fraud model not loaded")

        # Check cache
        data_hash = self._hash_data(transaction_data)
        cache_key = self._get_cache_key('return_fraud', data_hash)
        cached_result = self._get_from_cache(cache_key)

        if cached_result:
            cached_result['latency_ms'] = (time.time() - start_time) * 1000
            cached_result['cached'] = True
            return cached_result

        # Extract features
        features = self._extract_return_fraud_features(transaction_data)
        if features is None:
            return self._error_response("Failed to extract return fraud features")

        # Scale features
        features_scaled = self.scalers['return_fraud'].transform([features])[0]

        # Predict
        try:
            model = self.models['return_fraud']
            probability = float(model.predict_proba([features_scaled])[0][1])

            # Use optimal threshold from training
            threshold = 0.35  # This should be loaded from model metadata
            prediction = int(probability >= threshold)

            result = {
                'probability': probability,
                'prediction': prediction,
                'confidence': abs(probability - 0.5) * 2,
                'cached': False,
                'latency_ms': (time.time() - start_time) * 1000,
                'model_version': 'lr_v1',
                'threshold': threshold
            }

            # Cache the result
            self._set_to_cache(cache_key, result)

            return result

        except Exception as e:
            return self._error_response(f"Return fraud prediction error: {e}")

    def _extract_fraud_features(self, data: Dict) -> Optional[np.ndarray]:
        """Extract and order fraud detection features"""
        try:
            features = [
                data.get('transaction_amount', 0),
                data.get('amount_zscore', 0),
                data.get('velocity_count_1h', 0),
                data.get('velocity_count_24h', 0),
                data.get('velocity_amount_24h', 0),
                data.get('country_distance_km', 0),
                data.get('country_new', 0),
                data.get('state_count_24h', 0),
                data.get('device_new', 0),
                data.get('device_count', 0),
                data.get('device_velocity_24h', 0),
                data.get('hour_of_day', 0),
                data.get('day_of_week', 0),
                data.get('is_weekend', 0),
                data.get('is_night', 0),
                data.get('customer_age_days', 0),
                data.get('customer_txn_count', 0),
                data.get('customer_total_amount', 0),
                data.get('customer_chargeback_rate', 0),
                data.get('card_issuer_risk_score', 0),
                data.get('mcc_fraud_rate', 0),
                data.get('auth_3ds', 0),
                data.get('auth_avs_match', 0),
                data.get('auth_cvv_match', 0),
                data.get('email_domain_suspicious', 0),
                data.get('shipping_billing_mismatch', 0),
            ]
            return np.array(features, dtype=np.float32)
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None

    def _extract_chargeback_features(self, data: Dict) -> Optional[np.ndarray]:
        """Extract and order chargeback prediction features"""
        try:
            features = [
                data.get('transaction_amount', 0),
                data.get('transaction_days_old', 0),
                data.get('is_recurring', 0),
                data.get('mcc_code', 0),
                data.get('customer_age_days', 0),
                data.get('customer_txn_count', 0),
                data.get('customer_avg_txn_amount', 0),
                data.get('customer_lifetime_value', 0),
                data.get('customer_chargeback_history', 0),
                data.get('customer_dispute_rate', 0),
                data.get('merchant_category_risk', 0),
                data.get('merchant_chargeback_rate', 0),
                data.get('merchant_avg_txn_amount', 0),
                data.get('card_present', 0),
                data.get('auth_3ds', 0),
                data.get('auth_avs_match', 0),
                data.get('hour_of_day', 0),
                data.get('is_weekend', 0),
                data.get('has_tracking', 0),
                data.get('delivery_days', 0),
                data.get('refund_issued', 0),
            ]
            return np.array(features, dtype=np.float32)
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None

    def _extract_return_fraud_features(self, data: Dict) -> Optional[np.ndarray]:
        """Extract and order return fraud classification features"""
        try:
            features = [
                data.get('return_count', 0),
                data.get('return_rate', 0),
                data.get('high_value_return_count', 0),
                data.get('return_to_purchase_ratio', 0),
                data.get('customer_age_days', 0),
                data.get('customer_txn_count', 0),
                data.get('customer_lifetime_value', 0),
                data.get('customer_avg_txn_amount', 0),
                data.get('customer_return_fraud_history', 0),
                data.get('item_price', 0),
                data.get('item_category', 0),
                data.get('item_return_rate', 0),
                data.get('is_high_return_category', 0),
                data.get('return_days_from_purchase', 0),
                data.get('return_reason_suspicious', 0),
                data.get('item_condition_ok', 0),
                data.get('is_return_window_edge', 0),
                data.get('seasonal_high_return_period', 0),
            ]
            return np.array(features, dtype=np.float32)
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return None

    def _error_response(self, error_msg: str) -> Dict:
        """Return standardized error response"""
        return {
            'error': error_msg,
            'probability': 0,
            'prediction': 0,
            'confidence': 0,
            'cached': False,
            'latency_ms': 0
        }

    def batch_predict_fraud(self, transactions: list) -> list:
        """Batch predict fraud for multiple transactions"""
        results = []
        for txn in transactions:
            results.append(self.predict_fraud(txn))
        return results

    def batch_predict_chargeback(self, transactions: list) -> list:
        """Batch predict chargeback for multiple transactions"""
        results = []
        for txn in transactions:
            results.append(self.predict_chargeback(txn))
        return results

    def batch_predict_return_fraud(self, returns: list) -> list:
        """Batch predict return fraud for multiple returns"""
        results = []
        for ret in returns:
            results.append(self.predict_return_fraud(ret))
        return results

    def get_model_status(self) -> Dict:
        """Get status of all loaded models"""
        return {
            'fraud': 'loaded' if 'fraud' in self.models else 'not_loaded',
            'chargeback': 'loaded' if 'chargeback' in self.models else 'not_loaded',
            'return_fraud': 'loaded' if 'return_fraud' in self.models else 'not_loaded',
            'redis_connected': self.redis is not None,
            'cache_ttl_seconds': self.cache_ttl
        }


# Convenience functions for direct module usage
_inference_engine = None

def init_inference(models_dir: str = None, redis_client = None, cache_ttl: int = 3600) -> MLInferenceEngine:
    """Initialize inference engine"""
    global _inference_engine
    _inference_engine = MLInferenceEngine(models_dir, redis_client, cache_ttl)
    return _inference_engine

def predict_fraud(transaction_data: Dict) -> Dict:
    """Predict fraud for a transaction"""
    if _inference_engine is None:
        init_inference()
    return _inference_engine.predict_fraud(transaction_data)

def predict_chargeback(transaction_data: Dict) -> Dict:
    """Predict chargeback for a transaction"""
    if _inference_engine is None:
        init_inference()
    return _inference_engine.predict_chargeback(transaction_data)

def predict_return_fraud(transaction_data: Dict) -> Dict:
    """Predict return fraud for a transaction"""
    if _inference_engine is None:
        init_inference()
    return _inference_engine.predict_return_fraud(transaction_data)

def get_inference_status() -> Dict:
    """Get inference engine status"""
    if _inference_engine is None:
        return {'status': 'not_initialized'}
    return _inference_engine.get_model_status()
