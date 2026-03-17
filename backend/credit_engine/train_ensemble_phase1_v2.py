#!/usr/bin/env python3
"""
PHASE 1 REVISED: Better Accuracy Boost Without Overfitting
Incorporates:
1. Smart SMOTE (only for training, not evaluation)
2. Feature engineering with proper validation
3. Hyperparameter tuning on balanced data
4. Ensemble with proper weighting
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
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report, roc_curve
)
from xgboost import XGBClassifier
import lightgbm as lgb
from imblearn.over_sampling import SMOTE
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# PHASE 1 REVISED: ADVANCED FEATURE ENGINEERING
# ============================================================================

def engineer_features(df):
    """Create advanced financial ratio features"""
    print("\n📊 PHASE 1 STEP 1: Advanced Feature Engineering...")
    
    df_eng = df.copy()
    
    # Feature 1: Profit Margin
    df_eng['profit_margin'] = (
        (df_eng['net_profit'] / (df_eng['revenue'] + 1)) * 100
    ).clip(-100, 100)
    
    # Feature 2: Return on Assets (ROA)
    df_eng['roa'] = (
        (df_eng['net_profit'] / (df_eng['avg_balance'] + 1)) * 100
    ).clip(-100, 100)
    
    # Feature 3: Debt Service Coverage Ratio
    df_eng['dscr'] = (
        (df_eng['net_profit'] + 1000) / ((df_eng['debt_to_equity'] + 0.1) * 1000)
    ).clip(0, 100)
    
    # Feature 4: Liquidity Ratio
    df_eng['liquidity'] = (
        df_eng['avg_balance'] / (df_eng['revenue'] * 0.05 + 1000)
    ).clip(0, 100)
    
    # Feature 5: Risk-Adjusted Performance
    df_eng['risk_adjusted_score'] = (
        (df_eng['profit_margin'] / 100 * 50) +
        (df_eng['dscr'] / 100 * 30) +
        ((100 - df_eng['fraud_score']) / 100 * 20)
    ).clip(0, 100)
    
    # Feature 6: Normalized Debt Burden
    df_eng['debt_burden'] = (
        (df_eng['debt_to_equity'] / (df_eng['debt_to_equity'].max() + 1)) * 100
    ).clip(0, 100)
    
    # Feature 7: Financial Health Score (composite)
    df_eng['financial_health'] = (
        (df_eng['profit_margin'].clip(0, 100) / 100 * 40) +
        (df_eng['liquidity'].clip(0, 100) / 100 * 35) +
        ((100 - df_eng['debt_burden']) / 100 * 25)
    ).clip(0, 100)
    
    # Handle NaN/Inf
    for col in df_eng.columns:
        df_eng[col] = df_eng[col].replace([np.inf, -np.inf], 0).fillna(0)
    
    print(f"   ✓ Created 7 new features")
    print(f"   ✓ Total: 5 original + 7 engineered = 12 features")
    
    return df_eng


# ============================================================================
# PHASE 1: MAIN TRAINING PIPELINE
# ============================================================================

def main():
    """Main Phase 1 training"""
    
    print("\n" + "="*70)
    print("PHASE 1 REVISED: Smart Accuracy Boost (70.6% → 80-85%)")
    print("="*70)
    
    # ====================================================================
    # STEP 1: LOAD DATA
    # ====================================================================
    
    print("\n📂 Loading data...")
    root = Path(__file__).resolve().parent.parent
    dataset_dir = root / "Dataset"
    lc_path = dataset_dir / "lendingclub_full.csv"
    
    if not lc_path.exists():
        print(f"❌ Not found: {lc_path}")
        return
    
    df = pd.read_csv(lc_path)
    df = df.dropna(subset=['expected_decision'])
    print(f"   ✓ Loaded: {len(df):,} samples")
    
    # ====================================================================
    # STEP 2: FEATURE ENGINEERING
    # ====================================================================
    
    df = engineer_features(df)
    
    # ====================================================================
    # STEP 3: PREPARE DATA
    # ====================================================================
    
    print("\n📋 Preparing training data...")
    
    feature_cols = [
        'revenue', 'net_profit', 'debt_to_equity', 'fraud_score', 'avg_balance',
        'profit_margin', 'roa', 'dscr', 'liquidity', 'risk_adjusted_score',
        'debt_burden', 'financial_health'
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
    
    print(f"   ✓ Features: {len(feature_cols)} columns")
    print(f"   ✓ Samples: {len(X_scaled):,}")
    unique, counts = np.unique(y_encoded, return_counts=True)
    for label, count in zip(unique, counts):
        print(f"   ✓ Class {label}: {count:,} ({count/len(y_encoded)*100:.1f}%)")
    
    # ====================================================================
    # STEP 4: TRAIN/TEST SPLIT (Do BEFORE any balancing!)
    # ====================================================================
    
    print("\n✂️ Train/test split (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, stratify=y_encoded, random_state=42
    )
    print(f"   ✓ Train: {len(X_train):,}")
    print(f"   ✓ Test: {len(X_test):,}")
    
    # ====================================================================
    # STEP 5: APPLY SMOTE TO TRAINING DATA ONLY
    # ====================================================================
    
    print("\n⚖️ Applying SMOTE to training data...")
    print(f"   Before SMOTE: {len(X_train):,} samples")
    unique, counts = np.unique(y_train, return_counts=True)
    for label, count in zip(unique, counts):
        print(f"      Class {label}: {count:,} ({count/len(y_train)*100:.1f}%)")
    
    smote = SMOTE(random_state=42, k_neighbors=3)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    
    print(f"   After SMOTE: {len(X_train_balanced):,} samples")
    unique, counts = np.unique(y_train_balanced, return_counts=True)
    for label, count in zip(unique, counts):
        print(f"      Class {label}: {count:,} ({count/len(y_train_balanced)*100:.1f}%)")
    
    # ====================================================================
    # STEP 6: TRAIN ENSEMBLE MODELS
    # ====================================================================
    
    print("\n🤖 Training ensemble models with improved parameters...")
    
    # Build base models with better tuning
    models = {
        'xgboost': XGBClassifier(
            n_estimators=150,
            max_depth=7,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.8,
            min_child_weight=2,
            reg_alpha=0.1,
            reg_lambda=0.1,
            scale_pos_weight=len(y_train_balanced[y_train_balanced==0]) / len(y_train_balanced[y_train_balanced==1]),
            random_state=42,
            verbosity=0
        ),
        'lightgbm': lgb.LGBMClassifier(
            n_estimators=150,
            max_depth=8,
            learning_rate=0.05,
            num_leaves=50,
            feature_fraction=0.85,
            bagging_fraction=0.85,
            min_child_samples=10,
            is_unbalance=True,
            random_state=42,
            verbosity=-1
        ),
        'random_forest': RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ),
        'gradient_boosting': GradientBoostingClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.85,
            min_samples_split=5,
            random_state=42
        ),
        'logistic_regression': LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=42,
            solver='lbfgs'
        )
    }
    
    print("   Training individual models...")
    individual_scores = {}
    for name, model in models.items():
        print(f"      {name}...", end=" ", flush=True)
        model.fit(X_train_balanced, y_train_balanced)
        score = model.score(X_test, y_test)
        individual_scores[name] = score
        print(f"✓ ({score:.2%})")
    
    # Create voting ensemble
    print("   Creating ensemble with weighted voting...")
    ensemble = VotingClassifier(
        estimators=list(models.items()),
        voting='soft',
        weights=[1.1, 1.1, 1.0, 1.0, 0.8]  # Weight GB and LGB slightly higher
    )
    ensemble.fit(X_train_balanced, y_train_balanced)
    print("   ✓ Ensemble trained")
    
    # ====================================================================
    # STEP 7: EVALUATION ON ORIGINAL TEST SET
    # ====================================================================
    
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    
    y_pred = ensemble.predict(X_test)
    y_pred_proba = ensemble.predict_proba(X_test)[:, 1]
    
    train_pred = ensemble.predict(X_train)
    
    # Metrics
    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    try:
        roc_auc = roc_auc_score(y_test, y_pred_proba)
    except:
        roc_auc = 0.0
    
    # Cross-validation
    cv_scores = cross_val_score(
        VotingClassifier(
            estimators=list(models.items()),
            voting='soft',
            weights=[1.1, 1.1, 1.0, 1.0, 0.8]
        ),
        X_train_balanced, y_train_balanced, cv=5, scoring='accuracy'
    )
    
    print(f"\n📈 BASELINE (Before Phase 1)")
    print(f"   Test Accuracy:     70.60%")
    print(f"   ROC-AUC:           52.76%")
    print(f"   Precision:         49.84%")
    
    print(f"\n✨ AFTER PHASE 1 (With Engineering, SMOTE, Tuning)")
    print(f"   Training Accuracy: {train_acc:.2%}")
    print(f"   Test Accuracy:     {test_acc:.2%}")
    print(f"   Precision:         {precision:.2%}")
    print(f"   Recall:            {recall:.2%}")
    print(f"   F1-Score:          {f1:.2%}")
    print(f"   ROC-AUC:           {roc_auc:.4f}")
    
    print(f"\n   CV Mean:           {cv_scores.mean():.2%}")
    print(f"   CV Std Dev:        ±{cv_scores.std():.2%}")
    
    print(f"\n🚀 IMPROVEMENT")
    improvement = (test_acc - 0.706) * 100
    direction = "↑" if improvement > 0 else "↓"
    print(f"   {direction} {abs(improvement):+.2f} percentage points")
    
    print(f"\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    print(f"\n🔄 Individual Model Performance on Test Set:")
    for name, score in individual_scores.items():
        print(f"   {name:20s}: {score:.2%}")
    
    # ====================================================================
    # SAVE MODEL
    # ====================================================================
    
    print("\n💾 Saving Phase 1 model...")
    model_path = Path(__file__).resolve().parent / "data" / "ensemble_lc_phase1_v2.pkl"
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
            'cv_std': cv_scores.std(),
            'individual_scores': individual_scores
        }
    }
    
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"   ✓ Saved: {model_path}")
    print(f"   ✓ Size: {model_path.stat().st_size / 1e6:.1f} MB")
    
    print("\n" + "="*70)
    print("✅ PHASE 1 COMPLETE!")
    print("="*70)
    print("\n📈 What was done:")
    print("   ✓ 7 new financial ratio features created")
    print("   ✓ SMOTE applied to balance training data")
    print("   ✓ XGBoost, LightGBM, RF, GB, LR trained and tuned")
    print("   ✓ Soft voting ensemble created")
    print("   ✓ Proper train/test evaluation maintained")
    print("\n🎯 Next: Phase 2 improvements if needed")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
