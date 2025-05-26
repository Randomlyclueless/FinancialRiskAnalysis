# ml_models/predictor.py

import pickle
import os
import pandas as pd
from typing import Dict, Any

# Constants
MODEL_FILE = 'model.pkl'

# Required features from user input - these should match what your form collects
REQUIRED_FEATURES = ['term', 'int_rate', 'emp_length', 'loan_amount', 'income', 'expenses', 'emi']

class LoanPredictor:
    """Loan prediction service: loads the ML model once and exposes prediction methods."""
    def __init__(self):
        self.model = self._load_model()
        
    def _load_model(self):
        """Load the serialized ML model or raise an error if missing/corrupt."""
        model_path = os.path.join(os.path.dirname(__file__), MODEL_FILE)
        if not os.path.exists(model_path):
            raise RuntimeError(f"Model file not found at {model_path}")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
        
    def _validate_input(self, input_data: Dict[str, Any]):
        """Ensure all required features are present."""
        missing = [f for f in REQUIRED_FEATURES if f not in input_data]
        if missing:
            raise ValueError(f"Missing features: {missing}")
            
    def _preprocess_input(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """Convert input dictionary to DataFrame with expected columns."""
        # Convert to DataFrame with only the required columns
        df = pd.DataFrame([input_data])
        
        # Calculate additional features if needed
        # For example, if your model needs DTI (Debt-to-Income ratio) but it's not in the input
        if 'dti' not in df.columns and 'income' in df.columns and 'emi' in df.columns:
            df['dti'] = (df['emi'] / df['income']) * 100
            
        return df

    def predict_approval(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict loan approval (0 or 1) and its probability."""
        self._validate_input(input_data)
        df = self._preprocess_input(input_data)
        
        try:
            pred = self.model.predict(df)[0]
            prob = self.model.predict_proba(df)[0][1]
            return {
                "prediction": int(pred),
                "probability": round(float(prob), 4),
                "status": "approved" if pred == 1 else "rejected"
            }
        except Exception as e:
            import traceback
            print(f"Prediction error: {str(e)}")
            print(traceback.format_exc())
            raise RuntimeError(f"Failed to make prediction: {str(e)}")

    def predict_term(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return the loan term from input.
        """
        term = input_data.get('term')
        if term is None:
            raise ValueError("Missing 'term' input")
        return {"loan_term": int(term)}

    def predict_eligibility(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine loan eligibility based on debt-to-income ratio.
        Simple rule: eligible if EMI < 50% of income.
        """
        income = input_data.get('income')
        emi = input_data.get('emi')
        if income is None or emi is None:
            raise ValueError("Missing 'income' or 'emi' input")
        
        # Calculate debt-to-income ratio
        dti = (emi / income) * 100
        
        # Determine eligibility based on DTI
        if dti < 50:
            eligible = True
            message = "Your debt-to-income ratio is acceptable."
        else:
            eligible = False
            message = "Your debt-to-income ratio is too high."
            
        return {
            "eligible": eligible,
            "dti": round(dti, 2),
            "message": message
        }

# Single shared predictor instance
_predictor = LoanPredictor()

def predict_from_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Alias to the primary approval-prediction method."""
    return _predictor.predict_approval(input_data)

def predict_loan_approval(input_data: Dict[str, Any]) -> Dict[str, Any]:
    return _predictor.predict_approval(input_data)

def predict_loan_term(input_data: Dict[str, Any]) -> Dict[str, Any]:
    return _predictor.predict_term(input_data)

def predict_loan_eligibility(input_data: Dict[str, Any]) -> Dict[str, Any]:
    return _predictor.predict_eligibility(input_data)