"""Train XGBoost classifier with engineered features."""

import pandas as pd
from pathlib import Path
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import yaml
import numpy as np


def load_config():
    root = Path(__file__).resolve().parent
    config_path = root / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def train_scorer_engineered():
    config = load_config()
    data_path = Path(__file__).parent / "data" / "labeled_scorer_data_engineered.csv"
    model_path = Path(__file__).parent / "data" / "scorer_model_engineered.pkl"

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

    # Use best parameters from previous tuning
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.01,
        subsample=1.0,
        colsample_bytree=0.8,
        min_child_weight=1,
        random_state=42,
        eval_metric='logloss'
    )

    model.fit(X_train, y_train)

    # Evaluate on test set
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\nTest Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['REJECT', 'APPROVE']))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Cross-validation on full training data
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    print(f"\nCross-validation scores: {cv_scores}")
    print(f"Mean CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")

    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("\nTop 10 Feature Importances:")
    print(feature_importance.head(10))

    # Save model and scaler
    joblib.dump(model, model_path)
    joblib.dump(scaler, Path(__file__).parent / "data" / "scaler_engineered.pkl")
    print(f"\nModel saved to {model_path}")
    print(f"Scaler saved to {Path(__file__).parent / 'data' / 'scaler_engineered.pkl'}")


if __name__ == "__main__":
    train_scorer_engineered()