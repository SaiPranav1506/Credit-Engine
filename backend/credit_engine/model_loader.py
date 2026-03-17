"""
Model Loader for Production Deployment
Handles loading the best trained model with proper fallback and error handling
"""

import pickle
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ModelLoader:
    """Load and manage the production credit decision model"""
    
    VERSION = "3.0"
    MODEL_NAME = "ensemble_phase3_optimized"
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize model loader
        
        Args:
            model_dir: Directory containing model files. Defaults to credit_engine/data
        """
        if model_dir is None:
            model_dir = Path(__file__).parent / "credit_engine" / "data"
        else:
            model_dir = Path(model_dir)
            
        self.model_dir = model_dir
        self.model = None
        self.threshold = 0.5
        self.scaler = None
        self.label_encoder = None
        
    def load(self) -> bool:
        """
        Load production model with fallback strategy
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        models_to_try = [
            ("ensemble_phase3_optimized", "phase3_threshold.npy"),
            ("ensemble_phase2b_features", None),
            ("ensemble_phase1_improved", None),
        ]
        
        for model_name, threshold_file in models_to_try:
            try:
                model_path = self.model_dir / f"{model_name}.pkl"
                if not model_path.exists():
                    logger.warning(f"Model not found at {model_path}")
                    continue
                    
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                    
                logger.info(f"Successfully loaded model: {model_name}")
                
                # Try to load threshold if available
                if threshold_file:
                    threshold_path = self.model_dir / threshold_file
                    if threshold_path.exists():
                        self.threshold = float(np.load(threshold_path))
                        logger.info(f"Loaded threshold: {self.threshold:.2f}")
                
                return True
                
            except Exception as e:
                logger.warning(f"Failed to load {model_name}: {str(e)}")
                continue
        
        logger.error("All model loading attempts failed")
        return False
        
    def predict(self, X) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on input data
        
        Args:
            X: Feature matrix (must be scaled and preprocessed)
            
        Returns:
            Tuple of (predictions, probabilities)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
            
        try:
            # Get probability predictions
            proba = self.model.predict_proba(X)[:, 1]
            
            # Apply threshold
            predictions = (proba >= self.threshold).astype(int)
            
            return predictions, proba
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    def get_model_info(self) -> dict:
        """Get information about loaded model"""
        return {
            "version": self.VERSION,
            "model_name": self.MODEL_NAME,
            "threshold": self.threshold,
            "model_type": type(self.model).__name__ if self.model else None,
            "status": "loaded" if self.model else "not_loaded"
        }


def load_production_model(model_dir: Optional[str] = None) -> Optional[ModelLoader]:
    """
    Utility function to load production model
    
    Returns:
        ModelLoader instance if successful, None otherwise
    """
    loader = ModelLoader(model_dir)
    if loader.load():
        return loader
    return None
