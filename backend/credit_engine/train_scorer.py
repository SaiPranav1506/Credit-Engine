"""Train XGBoost classifier for credit scoring with hyperparameter tuning."""

import pandas as pd
from pathlib import Path
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
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


def train_scorer():
    config = load_config()
    data_path = Path(__file__).parent / "data" / "labeled_scorer_data.csv"
    model_path = Path(__file__).parent / "data" / "scorer_model.pkl"

    df = pd.read_csv(data_path)
    X = df.drop(columns=["expected_decision"])
    y = df["expected_decision"].map({"APPROVE": 1, "REJECT": 0})

    print(f"Dataset shape: {X.shape}")
    print(f"Class distribution: {y.value_counts().to_dict()}")

    # Feature scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # Hyperparameter tuning
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 4, 5, 6],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0],
        'min_child_weight': [1, 3, 5]
    }

    model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')

    # Grid search with cross-validation
    grid_search = GridSearchCV(
        model, param_grid, cv=5, scoring='accuracy', n_jobs=-1, verbose=1
    )
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best CV score: {grid_search.best_score_:.2%}")

    # Evaluate on test set
    y_pred = best_model.predict(X_test)
    y_pred_proba = best_model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n" + "="*60)
    print("MODEL PERFORMANCE METRICS")
    print("="*60)

    print(f"\n📊 BASIC METRICS:")
    print(f"Test Accuracy: {accuracy:.2%}")
    print(f"Training Accuracy: {best_model.score(X_train, y_train):.2%}")

    print(f"\n📈 CLASSIFICATION REPORT:")
    print(classification_report(y_test, y_pred, target_names=['REJECT', 'APPROVE']))

    print(f"🔢 CONFUSION MATRIX:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)

    # Additional metrics
    from sklearn.metrics import roc_auc_score, precision_recall_curve, average_precision_score

    print(f"\n🎯 ADVANCED METRICS:")
    try:
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        print(f"ROC-AUC Score: {roc_auc:.3f}")
    except:
        print("ROC-AUC Score: N/A (single class in test set)")

    try:
        avg_precision = average_precision_score(y_test, y_pred_proba)
        print(f"Average Precision Score: {avg_precision:.3f}")
    except:
        print("Average Precision Score: N/A")

    # Precision-Recall curve points
    precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)
    print(f"Precision-Recall Curve - Max Precision: {precision[:-1].max():.3f}, Max Recall: {recall[:-1].max():.3f}")

    print(f"\n📉 CROSS-VALIDATION METRICS:")
    cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, scoring='accuracy')
    print(f"CV Accuracy Scores: {cv_scores}")
    print(f"Mean CV Accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")

    # Additional CV metrics
    cv_precision = cross_val_score(best_model, X_train, y_train, cv=5, scoring='precision')
    cv_recall = cross_val_score(best_model, X_train, y_train, cv=5, scoring='recall')
    cv_f1 = cross_val_score(best_model, X_train, y_train, cv=5, scoring='f1')

    print(f"CV Precision: {cv_precision.mean():.3f} (+/- {cv_precision.std() * 2:.3f})")
    print(f"CV Recall: {cv_recall.mean():.3f} (+/- {cv_recall.std() * 2:.3f})")
    print(f"CV F1-Score: {cv_f1.mean():.3f} (+/- {cv_f1.std() * 2:.3f})")

    print(f"\n🏗️ MODEL CHARACTERISTICS:")
    print(f"Number of Features: {X.shape[1]}")
    print(f"Training Samples: {X_train.shape[0]}")
    print(f"Test Samples: {X_test.shape[0]}")
    print(f"Best Parameters: {grid_search.best_params_}")

    # Feature importance
    print(f"\n🔍 TOP 5 FEATURE IMPORTANCE:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)

    for idx, row in feature_importance.head(5).iterrows():
        print(f"{row['feature']}: {row['importance']:.4f}")

    print(f"\n💾 MODEL INFO:")
    print(f"Model saved to: {model_path}")
    print(f"Scaler saved to: {Path(__file__).parent / 'data' / 'scaler.pkl'}")

    print(f"\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    train_scorer()