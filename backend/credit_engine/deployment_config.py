"""
Deployment Configuration and Guide for Credit Engine Model
Version: 3.0 (Production Ready)
"""

import os
from pathlib import Path

class DeploymentConfig:
    """Production deployment configuration"""
    
    # Model settings
    MODEL_VERSION = "3.0"
    MODEL_NAME = "ensemble_phase3_optimized"
    
    # Model performance metrics
    METRICS = {
        "accuracy": 0.7798,
        "precision": 0.9299,
        "recall": 0.2748,
        "f1_score": 0.4242,
        "roc_auc": 0.7360,
        "train_accuracy": 0.7906,
    }
    
    # Features required for prediction
    REQUIRED_FEATURES = [
        'revenue',
        'net_profit',
        'debt_to_equity',
        'fraud_score',
        'avg_balance'
    ]
    
    # Feature preprocessing
    FEATURE_SCALING = "StandardScaler"
    
    # Prediction threshold
    PREDICTION_THRESHOLD = 0.5
    
    # API configuration
    API_PORT = os.getenv('API_PORT', 5000)
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Model directories
    MODEL_DIR = Path(__file__).parent / "data"
    MODEL_PATH = MODEL_DIR / f"{MODEL_NAME}.pkl"
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'deployment.log')
    
    @classmethod
    def validate(cls):
        """Validate deployment configuration"""
        errors = []
        
        # Check required features
        if not cls.REQUIRED_FEATURES:
            errors.append("No required features defined")
        
        # Check model path exists
        if not cls.MODEL_PATH.exists():
            errors.append(f"Model file not found at {cls.MODEL_PATH}")
        
        # Check threshold validity
        if not (0 <= cls.PREDICTION_THRESHOLD <= 1):
            errors.append(f"Invalid threshold: {cls.PREDICTION_THRESHOLD}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_summary(cls):
        """Get deployment configuration summary"""
        return {
            "model_version": cls.MODEL_VERSION,
            "model_name": cls.MODEL_NAME,
            "accuracy": f"{cls.METRICS['accuracy']:.2%}",
            "features_count": len(cls.REQUIRED_FEATURES),
            "features": cls.REQUIRED_FEATURES,
            "threshold": cls.PREDICTION_THRESHOLD,
            "api_endpoint": f"http://{cls.API_HOST}:{cls.API_PORT}",
        }


"""
=============================================================================
DEPLOYMENT GUIDE
=============================================================================

1. PREREQUISITES
   - Python 3.8+
   - All dependencies installed: pip install -r credit_engine/requirements.txt
   - Model file available: credit_engine/data/ensemble_phase3_optimized.pkl

2. QUICK START

   from credit_engine.model_loader import load_production_model
   from credit_engine.deployment_config import DeploymentConfig
   import pandas as pd
   from sklearn.preprocessing import StandardScaler
   
   # Load model
   loader = load_production_model()
   scaler = StandardScaler()
   
   # Prepare features
   X = pd.DataFrame({
       'revenue': [50000],
       'net_profit': [5000],
       'debt_to_equity': [0.5],
       'fraud_score': [0.2],
       'avg_balance': [10000]
   })
   
   # Scale features
   X_scaled = scaler.fit_transform(X)
   
   # Make prediction
   predictions, probabilities = loader.predict(X_scaled)
   decision = 'APPROVE' if predictions[0] == 1 else 'REJECT'
   confidence = probabilities[0]
   
   print(f"Decision: {decision} (Confidence: {confidence:.2%})")

3. API DEPLOYMENT

   Run the Flask API server:
   $ python api.py
   
   Then make requests to:
   - POST /api/process-application
   - GET /api/health

4. DOCKER DEPLOYMENT

   Build image:
   $ docker build -t credit-engine:3.0 .
   
   Run container:
   $ docker run -p 5000:5000 credit-engine:3.0

5. MONITORING

   Key metrics to track:
   - Model accuracy: {:.2%}
   - Precision (avoid false positives): {:.2%}
   - Recall (catch defaults): {:.2%}
   - Prediction latency: < 100ms target
   - API uptime: 99.9%+ target

6. MODEL UPDATES

   To use a different model version:
   1. Place new model file in credit_engine/data/
   2. Update MODEL_NAME in DeploymentConfig
   3. Restart API server
   4. Models are tried in fallback order if primary fails

7. TROUBLESHOOTING

   If model prediction is slow:
   - Check n_jobs=-1 in ensemble estimators
   - Consider model quantization for CPU inference
   
   If predictions are off:
   - Verify input features match REQUIRED_FEATURES exactly
   - Check feature scaling is applied (use provided scaler)
   - Review decision threshold (default 0.5)

=============================================================================
""".format(
    DeploymentConfig.METRICS['accuracy'],
    DeploymentConfig.METRICS['precision'],
    DeploymentConfig.METRICS['recall']
)

if __name__ == "__main__":
    print("Deployment Configuration for Credit Engine Model v3.0")
    print("=" * 70)
    
    is_valid, errors = DeploymentConfig.validate()
    
    if is_valid:
        print("✓ Configuration is valid")
        print("\nSummary:")
        for key, value in DeploymentConfig.get_summary().items():
            print(f"  {key}: {value}")
    else:
        print("✗ Configuration has errors:")
        for error in errors:
            print(f"  - {error}")
