import os
import joblib
import warnings

# Suppress minor version warning between Colab and local scikit-learn
warnings.filterwarnings("ignore", category=UserWarning)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

# Predefined categories from transactions.csv for quick fallback
FALLBACK_CATEGORIES = [
    "Education",
    "Entertainment",
    "Fees",
    "Groceries",
    "Healthcare",
    "Income",
    "Insurance",
    "Mortgage",
    "Personal Care",
    "Rent",
    "Restaurants",
    "Shopping",
    "Subscription",
    "Transportation",
    "Travel",
    "Utilities",
    "Other"
]

_cached_model = None
_cached_categories = None

def load_model():
    """Loads the trained scikit-learn pipeline from model.joblib."""
    global _cached_model, _cached_categories
    if _cached_model is not None:
        return _cached_model
    
    if os.path.exists(MODEL_PATH):
        try:
            _cached_model = joblib.load(MODEL_PATH)
            # Try to retrieve classes from classifier step
            if hasattr(_cached_model, "classes_"):
                _cached_categories = sorted(list(_cached_model.classes_))
            elif hasattr(_cached_model, "named_steps") and "clf" in _cached_model.named_steps:
                clf = _cached_model.named_steps["clf"]
                if hasattr(clf, "classes_"):
                    _cached_categories = sorted(list(clf.classes_))
            return _cached_model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    return None

def get_categories():
    """Returns sorted list of all available categories."""
    global _cached_categories
    if _cached_categories:
        return _cached_categories
    
    model = load_model()
    if _cached_categories:
        return _cached_categories
    return sorted(FALLBACK_CATEGORIES)

def predict_category(description: str) -> dict:
    """
    Predicts the category for a given transaction description.
    Returns:
        dict: {
            "predicted_category": str,
            "confidence": float (0.0 to 1.0) or None,
            "success": bool
        }
    """
    if not description or not description.strip():
        return {"predicted_category": "Shopping", "confidence": 0.0, "success": False}
        
    model = load_model()
    if model is None:
        return {"predicted_category": "Shopping", "confidence": 0.0, "success": False}
        
    try:
        clean_text = description.strip()
        pred = model.predict([clean_text])[0]
        
        confidence = 0.0
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba([clean_text])[0]
            confidence = float(max(probs))
            
        return {
            "predicted_category": str(pred),
            "confidence": round(confidence, 2),
            "success": True
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return {"predicted_category": "Shopping", "confidence": 0.0, "success": False}
