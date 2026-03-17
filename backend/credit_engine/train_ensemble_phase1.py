#!/usr/bin/env python3
"""
PHASE 1: Quick Wins to Boost Accuracy from 70.6% to 80-85%
Incorporates:
1. SMOTE for class imbalance handling
2. Advanced feature engineering (new financial ratios)
3. Class weights in models
4. LightGBM addition to ensemble
5. Quick hyperparameter tuning with Optuna
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import sys
from datetime import datetime

# ML imports
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report
)
from xgboost import XGBClassifier
import lightgbm as lgb
from imblearn.over_sampling import SMOTE
import optuna
from optuna.pruners import MedianPruner
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# PHASE 1 STEP 1: ADVANCED FEATURE ENGINEERING
# ============================================================================

def engineer_features(df):
    """
    Create advanced financial ratio features to improve model discrimination
    Features created:
    1. Profit margin ratio
    2. Debt service capacity  
    3. Working capital ratio
    4. Asset efficiency
    5. Risk score combination
    """
    print("\n📊 PHASE 1 STEP 2: Advanced Feature Engineering...")
    
    df_engineered = df.copy()
    
    # Existing features
    # revenue, net_profit, debt_to_equity, fraud_score, avg_balance
    
    # New Feature 1: Profit Margin (%)
    # Higher profit margin = more capacity to service debt
    df_engineered['profit_margin'] = (
        (df_engineered['net_profit'] / (df_engineered['revenue'] + 1)) * 100
    ).round(2)
    
    # New Feature 2: Return on Assets (ROA)
    # How efficiently the company uses assets
    df_engineered['roa'] = (
        (df_engineered['net_profit'] / (df_engineered['avg_balance'] + 1)) * 100
    ).round(2)
    
    # New Feature 3: Debt Service Coverage Ratio (DSCR)
    # Can the company cover its debt obligations?
    df_engineered['dscr'] = (
        (df_engineered['net_profit'] + 1) / (df_engineered['debt_to_equity'] + 0.1)
    ).round(2)
    
    # New Feature 4: Capital Adequacy (Balance to Debt Ratio)
    # How much cash reserve relative to debt?
    df_engineered['capital_adequacy'] = (
        (df_engineered['avg_balance'] / (df_engineered['debt_to_equity'] * 
         df_engineered['revenue'] + 1)) * 100
    ).round(2)
    
    # New Feature 5: Financial Stability Index
    # Combination of profitability, liquidity, and leverage
    stability_score = (
        (df_engineered['profit_margin'].clip(0, 100) / 100 * 40) +  # Profitability (40%)
        (df_engineered['avg_balance'] / (df_engineered['revenue'] + 1) * 40) +  # Liquidity (40%)
        ((1 / (df_engineered['debt_to_equity'] + 1)) * 20)  # Leverage (20%)
    )
    df_engineered['financial_stability'] = stability_score.round(2)
    
    # New Feature 6: Fraud Risk Adjusted Score
    # Adjust fraud score by financial health
    df_engineered['fraud_adjusted'] = (
        df_engineered['fraud_score'] / (df_engineered['financial_stability'] + 1)
    ).round(2)
    
    # Handle infinite and NaN values
    for col in df_engineered.columns:
        df_engineered[col] = df_engineered[col].replace([np.inf, -np.inf], 0)
        df_engineered[col] = df_engineered[col].fillna(0)
    
    print(f"   ✓ Created 6 new financial ratio features")
    print(f"   ✓ Total features: 5 original + 6 new = 11 total")
    print(f"   New features:")
    print(f"      - Profit Margin")
    print(f"      - Return on Assets (ROA)")
    print(f"      - Debt Service Coverage Ratio (DSCR)")
    print(f"      - Capital Adequacy")
    print(f"      - Financial Stability Index")
    print(f"      - Fraud Risk Adjusted Score")
    
    return df_engineered


# ============================================================================
# PHASE 1 STEP 1: CLASS IMBALANCE HANDLING WITH SMOTE
# ============================================================================

def apply_smote(X_train, y_train):
    """
    Apply SMOTE (Synthetic Minority Over-sampling) to handle class imbalance
    This creates synthetic samples for minority class
    """
    print("\n⚖️ PHASE 1 STEP 1: Handling Class Imbalance with SMOTE...")
    
    print(f"   Before SMOTE:")
    unique, counts = np.unique(y_train, return_counts=True)
    for label, count in zip(unique, counts):
        pct = count / len(y_train) * 100
        print(f"      Class {label}: {count} samples ({pct:.1f}%)")
    
    # Apply SMOTE
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    
    print(f"\n   After SMOTE:")
    unique, counts = np.unique(y_resampled, return_counts=True)
    for label, count in zip(unique, counts):
        pct = count / len(y_resampled) * 100
        print(f"      Class {label}: {count} samples ({pct:.1f}%)")
    
    print(f"   ✓ SMOTE applied successfully (+{len(X_resampled) - len(X_train)} synthetic samples)")
    
    return X_resampled, y_resampled


# ============================================================================
# PHASE 1 STEP 4: HYPERPARAMETER TUNING WITH OPTUNA
# ============================================================================

def objective_xgboost(trial, X_train, y_train, X_val, y_val):
    """Optuna objective function for XGBoost hyperparameter tuning"""
    params = {
        'max_depth': trial.suggest_int('max_depth', 4, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 100, 300, step=50),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 5),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 1.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.0, 1.0),
        'gamma': trial.suggest_float('gamma', 0.0, 1.0),
    }
    
    model = XGBClassifier(
        **params,
        random_state=42,
        verbosity=0,
        scale_pos_weight=len(y_train[y_train == 0]) / len(y_train[y_train == 1])
    )
    
    model.fit(X_train, y_train)
    score = model.score(X_val, y_val)
    
    return score


def objective_lightgbm(trial, X_train, y_train, X_val, y_val):
    """Optuna objective function for LightGBM hyperparameter tuning"""
    params = {
        'max_depth': trial.suggest_int('max_depth', 4, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 100, 300, step=50),
        'num_leaves': trial.suggest_int('num_leaves', 20, 100),
        'feature_fraction': trial.suggest_float('feature_fraction', 0.6, 1.0),
        'bagging_fraction': trial.suggest_float('bagging_fraction', 0.6, 1.0),
        'min_child_samples': trial.suggest_int('min_child_samples', 5, 30),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 1.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.0, 1.0),
    }
    
    model = lgb.LGBMClassifier(
        **params,
        random_state=42,
        verbosity=-1,
        scale_pos_weight=len(y_train[y_train == 0]) / len(y_train[y_train == 1])
    )
    
    model.fit(X_train, y_train)
    score = model.score(X_val, y_val)
    
    return score


def tune_hyperparameters(X_train, y_train, X_val, y_val):
    """
    Quick hyperparameter tuning with Optuna (50 iterations for speed)
    """
    print("\n⚙️ PHASE 1 STEP 5: Quick Hyperparameter Tuning with Optuna...")
    
    print("   Tuning XGBoost (25 iterations)...")
    study_xgb = optuna.create_study(
        direction='maximize',
        pruner=MedianPruner()
    )
    study_xgb.optimize(
        lambda trial: objective_xgboost(trial, X_train, y_train, X_val, y_val),
        n_trials=25,
        show_progress_bar=False
    )
    
    best_xgb_params = study_xgb.best_params
    print(f"   ✓ Best XGBoost score: {study_xgb.best_value:.4f}")
    
    print("   Tuning LightGBM (25 iterations)...")
    study_lgb = optuna.create_study(
        direction='maximize',
        pruner=MedianPruner()
    )
    study_lgb.optimize(
        lambda trial: objective_lightgbm(trial, X_train, y_train, X_val, y_val),
        n_trials=25,
        show_progress_bar=False
    )
    
    best_lgb_params = study_lgb.best_params
    print(f"   ✓ Best LightGBM score: {study_lgb.best_value:.4f}")
    
    return best_xgb_params, best_lgb_params


# ============================================================================
# PHASE 1 STEP 3: TRAIN ENSEMBLE WITH BEST MODELS
# ============================================================================

def train_ensemble_phase1(X_train, y_train, X_test, y_test, best_xgb_params, best_lgb_params):
    """
    Train improved ensemble with:
    - XGBoost with class weights
    - LightGBM (new!)
    - Random Forest with class weights
    - Logistic Regression
    - SVM
    """
    print("\n🤖 PHASE 1 STEP 3: Training Improved Ensemble...")
    
    # Calculate class weights
    class_weights = {
        0: len(y_train) / (2 * np.sum(y_train == 0)),
        1: len(y_train) / (2 * np.sum(y_train == 1))
    }
    scale_pos_weight = class_weights[0] / class_weights[1]
    
    # XGBoost with class weights and tuned parameters
    xgb_params = best_xgb_params.copy()
    xgb_params.update({
        'scale_pos_weight': scale_pos_weight,
        'random_state': 42,
        'verbosity': 0
    })
    xgb_model = XGBClassifier(**xgb_params)
    
    # LightGBM with class weights and tuned parameters
    lgb_params = best_lgb_params.copy()
    lgb_params.update({
        'scale_pos_weight': scale_pos_weight,
        'random_state': 42,
        'verbosity': -1
    })
    lgb_model = lgb.LGBMClassifier(**lgb_params)
    
    # Random Forest with class weights
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    # Logistic Regression with class weights
    lr_model = LogisticRegression(
        max_iter=1000,
        class_weight='balanced',
        random_state=42
    )
    
    # SVM with class weights
    svm_model = SVC(
        kernel='rbf',
        probability=True,
        class_weight='balanced',
        random_state=42
    )
    
    print("   Training individual models...")
    models_list = [
        ('xgboost', xgb_model),
        ('lightgbm', lgb_model),
        ('random_forest', rf_model),
        ('logistic_regression', lr_model),
        ('svm', svm_model)
    ]
    
    for name, model in models_list:
        print(f"      {name}...", end=" ", flush=True)
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        print(f"✓ ({score:.2%})")
    
    # Create ensemble with soft voting
    print("   Creating soft voting ensemble...")
    ensemble = VotingClassifier(
        estimators=models_list,
        voting='soft',
        weights=[1.2, 1.2, 1.0, 1.0, 1.0]  # Slight weight to XGB and LGB
    )
    ensemble.fit(X_train, y_train)
    
    print("   ✓ Ensemble trained successfully")
    
    return ensemble, models_list


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def load_and_prepare_data():
    """Load and prepare training data"""
    print("\n" + "="*70)
    print("PHASE 1: Quick Accuracy Boost (70.6% → 80-85%)")
    print("="*70)
    
    print("\n📂 Step 1: Loading data...")
    root = Path(__file__).resolve().parent.parent
    dataset_dir = root / "Dataset"
    
    lc_path = dataset_dir / "lendingclub_full.csv"
    
    if not lc_path.exists():
        print(f"❌ File not found: {lc_path}")
        return None, None
    
    df = pd.read_csv(lc_path)
    print(f"   ✓ Loaded: {len(df):,} samples from {lc_path.name}")
    
    # Clean data
    df = df.dropna(subset=['expected_decision'])
    print(f"   ✓ After cleaning: {len(df):,} samples")
    
    # Engineer features
    df = engineer_features(df)
    
    # Prepare features
    print("\n📋 Preparing features...")
    feature_cols = [
        'revenue', 'net_profit', 'debt_to_equity', 'fraud_score', 'avg_balance',
        'profit_margin', 'roa', 'dscr', 'capital_adequacy', 
        'financial_stability', 'fraud_adjusted'
    ]
    
    X = df[feature_cols].copy()
    y = df['expected_decision'].copy()
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    print(f"   ✓ Features: {X_scaled.shape[1]} columns (5 original + 6 engineered)")
    print(f"   ✓ Samples: {len(X_scaled):,}")
    print(f"   ✓ Classes: APPROVE={sum(y_encoded==0)}, REJECT={sum(y_encoded==1)}")
    
    return X_scaled, y_encoded, le, scaler, feature_cols


def main():
    """Main pipeline"""
    try:
        # Load and prepare data
        result = load_and_prepare_data()
        if result[0] is None:
            return
        
        X, y, le, scaler, feature_cols = result
        
        # Train/test split (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        
        # PHASE 1 STEP 1: Apply SMOTE to training data
        X_train_smote, y_train_smote = apply_smote(X_train, y_train)
        
        # Create validation set from training data for hyperparameter tuning
        X_train_small, X_val, y_train_small, y_val = train_test_split(
            X_train_smote, y_train_smote, test_size=0.2, stratify=y_train_smote, random_state=42
        )
        
        # PHASE 1 STEP 5: Hyperparameter tuning
        best_xgb_params, best_lgb_params = tune_hyperparameters(
            X_train_small, y_train_small, X_val, y_val
        )
        
        # PHASE 1 STEP 3: Train ensemble
        ensemble, _ = train_ensemble_phase1(
            X_train_smote, y_train_smote, X_test, y_test, 
            best_xgb_params, best_lgb_params
        )
        
        # ====================================================================
        # EVALUATION
        # ====================================================================
        
        print("\n" + "="*70)
        print("📊 RESULTS COMPARISON")
        print("="*70)
        
        # Predictions
        y_pred_train = ensemble.predict(X_train_smote)
        y_pred_test = ensemble.predict(X_test)
        y_pred_proba = ensemble.predict_proba(X_test)[:, 1]
        
        # Metrics
        train_acc = accuracy_score(y_train_smote, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)
        precision = precision_score(y_test, y_pred_test, zero_division=0)
        recall = recall_score(y_test, y_pred_test, zero_division=0)
        f1 = f1_score(y_test, y_pred_test, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        # Cross-validation
        cv_scores = cross_val_score(ensemble, X_train_smote, y_train_smote, cv=5)
        
        print(f"\n🎯 BEFORE (Baseline)")
        print(f"   Training Accuracy: 71.08%")
        print(f"   Test Accuracy:     70.60%")
        print(f"   ROC-AUC:           52.76%")
        
        print(f"\n✨ AFTER (Phase 1 Improvements)")
        print(f"   Training Accuracy: {train_acc:.2%}")
        print(f"   Test Accuracy:     {test_acc:.2%}")
        print(f"   Precision:         {precision:.2%}")
        print(f"   Recall:            {recall:.2%}")
        print(f"   F1-Score:          {f1:.2%}")
        print(f"   ROC-AUC:           {roc_auc:.4f}")
        print(f"\n   CV Mean:           {cv_scores.mean():.2%}")
        print(f"   CV Std Dev:        ±{cv_scores.std():.2%}")
        
        improvement = (test_acc - 0.706) * 100
        print(f"\n🚀 IMPROVEMENT: +{improvement:.2f} percentage points")
        
        # Save model
        print("\n💾 Saving model...")
        root = Path(__file__).resolve().parent.parent
        model_path = root / "credit_engine" / "data" / "ensemble_lc_phase1.pkl"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'ensemble': ensemble,
            'scaler': scaler,
            'feature_cols': feature_cols,
            'label_encoder': le,
            'timestamp': datetime.now().isoformat(),
            'phase': 1,
            'metrics': {
                'test_accuracy': test_acc,
                'train_accuracy': train_acc,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'roc_auc': roc_auc,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"   ✓ Model saved: {model_path}")
        print(f"   ✓ File size: {model_path.stat().st_size / 1e6:.1f} MB")
        
        print("\n" + "="*70)
        print("✅ PHASE 1 COMPLETE!")
        print("="*70)
        print("\n📈 Next Steps:")
        print("   Phase 2: Medium Improvements (Add CatBoost, Feature Engineering)")
        print("   Phase 3: Final Push (Extended Tuning, Calibration)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
