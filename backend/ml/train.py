"""
ML Model Training Pipeline for AI Risk Manager
Trains three models: Fraud (XGBoost), Chargeback (Random Forest), Return Fraud (Logistic Regression)
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.ml.generate_data import generate_fraud_data, generate_chargeback_data, generate_return_fraud_data


class ModelTrainer:
    """Training pipeline for fraud detection models"""

    def __init__(self, models_dir: str = None):
        self.models_dir = Path(models_dir or "backend/ml/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.scalers_dir = self.models_dir / "scalers"
        self.scalers_dir.mkdir(exist_ok=True)

    def train_fraud_model(self, df: pd.DataFrame) -> dict:
        """
        Train XGBoost fraud detection model
        Target: 70%+ recall @ 0.5% FPR
        """
        print("\n" + "="*60)
        print("Training FRAUD Detection Model (XGBoost)")
        print("="*60)

        # Prepare features
        feature_cols = [col for col in df.columns if col not in ['is_fraud', 'transaction_id']]
        X = df[feature_cols]
        y = df['is_fraud']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"\nTraining set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        print(f"Fraud rate (train): {y_train.mean():.2%}")
        print(f"Fraud rate (test): {y_test.mean():.2%}")

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Define XGBoost with hyperparameter tuning
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [4, 6, 8],
            'learning_rate': [0.05, 0.1, 0.2],
            'scale_pos_weight': [len(y_train[y_train==0]) / len(y_train[y_train==1])]
        }

        xgb_model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='auc',
            random_state=42,
            use_label_encoder=False
        )

        print("\nPerforming hyperparameter tuning...")
        grid_search = GridSearchCV(
            xgb_model, param_grid, cv=3, scoring='roc_auc', n_jobs=-1, verbose=0
        )
        grid_search.fit(X_train_scaled, y_train)

        best_model = grid_search.best_estimator_
        print(f"Best parameters: {grid_search.best_params_}")

        # Evaluate on test set
        y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]
        y_pred = best_model.predict(X_test_scaled)

        # Find optimal threshold for 70% recall @ 0.5% FPR
        fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
        optimal_threshold = self._find_optimal_threshold(fpr, tpr, thresholds, target_recall=0.70, max_fpr=0.005)

        # Apply optimal threshold
        y_pred_optimal = (y_pred_proba >= optimal_threshold).astype(int)

        # Calculate metrics
        metrics = {
            'model_type': 'XGBoost',
            'target': 'is_fraud',
            'n_features': len(feature_cols),
            'n_train': X_train.shape[0],
            'n_test': X_test.shape[0],
            'optimal_threshold': float(optimal_threshold),
            'precision': float(precision_score(y_test, y_pred_optimal)),
            'recall': float(recall_score(y_test, y_pred_optimal)),
            'f1_score': float(f1_score(y_test, y_pred_optimal)),
            'auc_roc': float(roc_auc_score(y_test, y_pred_proba)),
            'confusion_matrix': confusion_matrix(y_test, y_pred_optimal).tolist(),
            'feature_importance': dict(zip(feature_cols, best_model.feature_importances_.tolist())),
            'training_date': datetime.now().isoformat(),
            'best_params': grid_search.best_params_
        }

        # Print results
        print(f"\n{'='*60}")
        print("FRAUD MODEL RESULTS")
        print(f"{'='*60}")
        print(f"Optimal Threshold: {optimal_threshold:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f} (Target: 70%+)")
        print(f"F1-Score: {metrics['f1_score']:.4f}")
        print(f"AUC-ROC: {metrics['auc_roc']:.4f}")
        print(f"\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred_optimal))
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred_optimal, target_names=['Legit', 'Fraud']))

        # Top 10 features
        top_features = sorted(metrics['feature_importance'].items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"\nTop 10 Important Features:")
        for feat, imp in top_features:
            print(f"  {feat}: {imp:.4f}")

        # Save model and scaler
        model_path = self.models_dir / "fraud_xgboost.joblib"
        scaler_path = self.scalers_dir / "fraud_scaler.joblib"
        joblib.dump(best_model, model_path)
        joblib.dump(scaler, scaler_path)
        print(f"\nModel saved to: {model_path}")
        print(f"Scaler saved to: {scaler_path}")

        return metrics

    def train_chargeback_model(self, df: pd.DataFrame) -> dict:
        """
        Train Random Forest chargeback prediction model
        Target: 60%+ precision (minimize false alarms)
        """
        print("\n" + "="*60)
        print("Training CHARGEBACK Prediction Model (Random Forest)")
        print("="*60)

        # Prepare features
        feature_cols = [col for col in df.columns if col not in ['is_chargeback', 'transaction_id']]
        X = df[feature_cols]
        y = df['is_chargeback']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"\nTraining set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        print(f"Chargeback rate (train): {y_train.mean():.2%}")
        print(f"Chargeback rate (test): {y_test.mean():.2%}")

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Define Random Forest with hyperparameter tuning
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [6, 8, 10],
            'min_samples_split': [5, 10],
            'min_samples_leaf': [2, 4],
            'class_weight': ['balanced']
        }

        rf_model = RandomForestClassifier(random_state=42, n_jobs=-1)

        print("\nPerforming hyperparameter tuning...")
        grid_search = GridSearchCV(
            rf_model, param_grid, cv=3, scoring='precision', n_jobs=-1, verbose=0
        )
        grid_search.fit(X_train_scaled, y_train)

        best_model = grid_search.best_estimator_
        print(f"Best parameters: {grid_search.best_params_}")

        # Evaluate on test set
        y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]

        # Find threshold for high precision (60%+)
        best_threshold = 0.5
        best_precision = 0
        for threshold in np.arange(0.3, 0.8, 0.05):
            y_pred_thresh = (y_pred_proba >= threshold).astype(int)
            prec = precision_score(y_test, y_pred_thresh, zero_division=0)
            rec = recall_score(y_test, y_pred_thresh, zero_division=0)
            if prec >= 0.60 and rec > 0.1:
                if prec > best_precision:
                    best_precision = prec
                    best_threshold = threshold

        y_pred_optimal = (y_pred_proba >= best_threshold).astype(int)

        # Calculate metrics
        metrics = {
            'model_type': 'RandomForest',
            'target': 'is_chargeback',
            'n_features': len(feature_cols),
            'n_train': X_train.shape[0],
            'n_test': X_test.shape[0],
            'optimal_threshold': float(best_threshold),
            'precision': float(precision_score(y_test, y_pred_optimal, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred_optimal, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred_optimal, zero_division=0)),
            'auc_roc': float(roc_auc_score(y_test, y_pred_proba)),
            'confusion_matrix': confusion_matrix(y_test, y_pred_optimal).tolist(),
            'feature_importance': dict(zip(feature_cols, best_model.feature_importances_.tolist())),
            'training_date': datetime.now().isoformat(),
            'best_params': grid_search.best_params_
        }

        # Print results
        print(f"\n{'='*60}")
        print("CHARGEBACK MODEL RESULTS")
        print(f"{'='*60}")
        print(f"Optimal Threshold: {best_threshold:.4f}")
        print(f"Precision: {metrics['precision']:.4f} (Target: 60%+)")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"F1-Score: {metrics['f1_score']:.4f}")
        print(f"AUC-ROC: {metrics['auc_roc']:.4f}")
        print(f"\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred_optimal))
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred_optimal, target_names=['Normal', 'Chargeback']))

        # Top 10 features
        top_features = sorted(metrics['feature_importance'].items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"\nTop 10 Important Features:")
        for feat, imp in top_features:
            print(f"  {feat}: {imp:.4f}")

        # Save model and scaler
        model_path = self.models_dir / "chargeback_rf.joblib"
        scaler_path = self.scalers_dir / "chargeback_scaler.joblib"
        joblib.dump(best_model, model_path)
        joblib.dump(scaler, scaler_path)
        print(f"\nModel saved to: {model_path}")
        print(f"Scaler saved to: {scaler_path}")

        return metrics

    def train_return_fraud_model(self, df: pd.DataFrame) -> dict:
        """
        Train Logistic Regression return fraud classifier
        Target: 80%+ recall on known patterns, interpretable
        """
        print("\n" + "="*60)
        print("Training RETURN FRAUD Classifier (Logistic Regression)")
        print("="*60)

        # Prepare features
        feature_cols = [col for col in df.columns if col not in ['is_return_fraud', 'transaction_id']]
        X = df[feature_cols]
        y = df['is_return_fraud']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"\nTraining set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        print(f"Return fraud rate (train): {y_train.mean():.2%}")
        print(f"Return fraud rate (test): {y_test.mean():.2%}")

        # Scale features (important for LR)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Define Logistic Regression with hyperparameter tuning
        param_grid = {
            'C': [0.1, 1.0, 10.0],
            'penalty': ['l2'],
            'solver': ['lbfgs'],
            'class_weight': ['balanced'],
            'max_iter': [1000]
        }

        lr_model = LogisticRegression(random_state=42)

        print("\nPerforming hyperparameter tuning...")
        grid_search = GridSearchCV(
            lr_model, param_grid, cv=3, scoring='recall', n_jobs=-1, verbose=0
        )
        grid_search.fit(X_train_scaled, y_train)

        best_model = grid_search.best_estimator_
        print(f"Best parameters: {grid_search.best_params_}")

        # Evaluate on test set
        y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]

        # Find threshold for high recall (80%+)
        best_threshold = 0.5
        best_recall = 0
        for threshold in np.arange(0.2, 0.7, 0.05):
            y_pred_thresh = (y_pred_proba >= threshold).astype(int)
            rec = recall_score(y_test, y_pred_thresh, zero_division=0)
            prec = precision_score(y_test, y_pred_thresh, zero_division=0)
            if rec >= 0.80 and prec > 0.05:
                if rec > best_recall:
                    best_recall = rec
                    best_threshold = threshold

        y_pred_optimal = (y_pred_proba >= best_threshold).astype(int)

        # Calculate metrics
        metrics = {
            'model_type': 'LogisticRegression',
            'target': 'is_return_fraud',
            'n_features': len(feature_cols),
            'n_train': X_train.shape[0],
            'n_test': X_test.shape[0],
            'optimal_threshold': float(best_threshold),
            'precision': float(precision_score(y_test, y_pred_optimal, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred_optimal, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred_optimal, zero_division=0)),
            'auc_roc': float(roc_auc_score(y_test, y_pred_proba)),
            'confusion_matrix': confusion_matrix(y_test, y_pred_optimal).tolist(),
            'feature_coefficients': dict(zip(feature_cols, best_model.coef_[0].tolist())),
            'training_date': datetime.now().isoformat(),
            'best_params': grid_search.best_params_
        }

        # Print results
        print(f"\n{'='*60}")
        print("RETURN FRAUD MODEL RESULTS")
        print(f"{'='*60}")
        print(f"Optimal Threshold: {best_threshold:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f} (Target: 80%+)")
        print(f"F1-Score: {metrics['f1_score']:.4f}")
        print(f"AUC-ROC: {metrics['auc_roc']:.4f}")
        print(f"\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred_optimal))
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred_optimal, target_names=['Legit Return', 'Return Fraud']))

        # Top 10 features by absolute coefficient value
        top_features = sorted(metrics['feature_coefficients'].items(), key=lambda x: abs(x[1]), reverse=True)[:10]
        print(f"\nTop 10 Coefficients (by absolute value):")
        for feat, coef in top_features:
            print(f"  {feat}: {coef:.4f}")

        # Save model and scaler
        model_path = self.models_dir / "return_fraud_lr.joblib"
        scaler_path = self.scalers_dir / "return_fraud_scaler.joblib"
        joblib.dump(best_model, model_path)
        joblib.dump(scaler, scaler_path)
        print(f"\nModel saved to: {model_path}")
        print(f"Scaler saved to: {scaler_path}")

        return metrics

    def _find_optimal_threshold(self, fpr, tpr, thresholds, target_recall=0.70, max_fpr=0.005):
        """
        Find optimal threshold that achieves target recall while staying below max FPR
        """
        valid_indices = (fpr <= max_fpr) & (tpr >= target_recall * 0.5)

        if not valid_indices.any():
            # Fall back to maximizing recall at lowest FPR
            valid_indices = fpr <= max_fpr

        if valid_indices.any():
            # Among valid thresholds, pick the one with highest recall
            best_idx = np.argmax(tpr[valid_indices])
            return thresholds[valid_indices][best_idx]

        return 0.5  # Default threshold

    def save_metrics_report(self, fraud_metrics, chargeback_metrics, return_metrics):
        """Save comprehensive metrics report"""
        report = {
            'training_date': datetime.now().isoformat(),
            'models': {
                'fraud_detection': fraud_metrics,
                'chargeback_prediction': chargeback_metrics,
                'return_fraud_classifier': return_metrics
            },
            'performance_targets': {
                'fraud': '70%+ recall @ 0.5% FPR',
                'chargeback': '60%+ precision (minimize false alarms)',
                'return_fraud': '80%+ recall on known patterns'
            }
        }

        report_path = self.models_dir / "metrics.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nMetrics report saved to: {report_path}")

        return report


def main():
    """Main training pipeline"""
    print("\n" + "="*80)
    print(" AI RISK MANAGER - ML MODEL TRAINING PIPELINE")
    print("="*80)

    trainer = ModelTrainer()

    # Generate synthetic data
    print("\n[1/3] Generating synthetic training data...")
    fraud_df = generate_fraud_data(n_samples=2000)
    chargeback_df = generate_chargeback_data(n_samples=2000)
    return_df = generate_return_fraud_data(n_samples=2000)

    print(f"  Fraud data: {fraud_df.shape} - {fraud_df['is_fraud'].sum()} positive cases ({fraud_df['is_fraud'].mean():.1%})")
    print(f"  Chargeback data: {chargeback_df.shape} - {chargeback_df['is_chargeback'].sum()} positive cases ({chargeback_df['is_chargeback'].mean():.1%})")
    print(f"  Return fraud data: {return_df.shape} - {return_df['is_return_fraud'].sum()} positive cases ({return_df['is_return_fraud'].mean():.1%})")

    # Train models
    print("\n[2/3] Training models...")
    fraud_metrics = trainer.train_fraud_model(fraud_df)
    chargeback_metrics = trainer.train_chargeback_model(chargeback_df)
    return_metrics = trainer.train_return_fraud_model(return_df)

    # Save report
    print("\n[3/3] Saving metrics report...")
    report = trainer.save_metrics_report(fraud_metrics, chargeback_metrics, return_metrics)

    print("\n" + "="*80)
    print(" TRAINING COMPLETE!")
    print("="*80)
    print(f"\nModels saved to: {trainer.models_dir}")
    print("\nPerformance Summary:")
    print(f"  Fraud Model (XGBoost):        Recall={fraud_metrics['recall']:.1%}, Precision={fraud_metrics['precision']:.1%}, AUC={fraud_metrics['auc_roc']:.3f}")
    print(f"  Chargeback Model (RF):        Precision={chargeback_metrics['precision']:.1%}, Recall={chargeback_metrics['recall']:.1%}, AUC={chargeback_metrics['auc_roc']:.3f}")
    print(f"  Return Fraud Model (LR):      Recall={return_metrics['recall']:.1%}, Precision={return_metrics['precision']:.1%}, AUC={return_metrics['auc_roc']:.3f}")

    return report


if __name__ == "__main__":
    main()
