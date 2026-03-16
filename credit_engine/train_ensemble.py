"""Ensemble model training for credit scoring."""

import pandas as pd
from pathlib import Path
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import joblib
import yaml
import numpy as np


def load_config():
    root = Path(__file__).resolve().parent
    config_path = root / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def train_ensemble_model():
    config = load_config()
    data_path = Path(__file__).parent / "data" / "labeled_scorer_data_engineered.csv"
    model_path = Path(__file__).parent / "data" / "ensemble_model.pkl"

    df = pd.read_csv(data_path)
    X = df.drop(columns=["expected_decision"])
    y = df["expected_decision"].map({"APPROVE": 1, "REJECT": 0})

    print(f"Dataset shape: {X.shape}")
    print(f"Class distribution: {y.value_counts().to_dict()}")

    # Handle any infinite or NaN values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.mean())

    # Feature scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split data with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # Create individual models
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.01,
        subsample=1.0,
        colsample_bytree=0.8,
        min_child_weight=1,
        random_state=42,
        eval_metric='logloss'
    )

    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )

    lr_model = LogisticRegression(random_state=42, max_iter=1000)

    svm_model = SVC(probability=True, random_state=42)

    # Create ensemble model
    ensemble = VotingClassifier(
        estimators=[
            ('xgb', xgb_model),
            ('rf', rf_model),
            ('lr', lr_model),
            ('svm', svm_model)
        ],
        voting='soft'  # Use probability-based voting
    )

    ensemble.fit(X_train, y_train)

    # Evaluate on test set
    y_pred = ensemble.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\nEnsemble Test Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['REJECT', 'APPROVE']))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Cross-validation
    cv_scores = cross_val_score(ensemble, X_train, y_train, cv=5, scoring='accuracy')
    print(f"\nCross-validation scores: {cv_scores}")
    print(f"Mean CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")

    # Compare individual models
    models = {
        'XGBoost': xgb_model,
        'Random Forest': rf_model,
        'Logistic Regression': lr_model,
        'SVM': svm_model,
        'Ensemble': ensemble
    }

    print("\nModel Comparison:")
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        acc = accuracy_score(y_test, pred)
        print(f"{name}: {acc:.2%}")

    # Save ensemble model and scaler
    joblib.dump(ensemble, model_path)
    joblib.dump(scaler, Path(__file__).parent / "data" / "scaler_ensemble.pkl")
    print(f"\nEnsemble model saved to {model_path}")
    print(f"Scaler saved to {Path(__file__).parent / 'data' / 'scaler_ensemble.pkl'}")


if __name__ == "__main__":
    train_ensemble_model()