"""
Machine Learning Model Module for Apex Zero Roster Optimizer

This module handles:
- Training Linear Regression and XGBoost models
- Model comparison and selection (RMSE-based)
- Performance prediction
- Value index calculation
- Model persistence

CLI Usage:
    python ml_model.py --train         # Train and save best model
    python ml_model.py --predict       # Load model and make predictions
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import os
import argparse
import warnings
warnings.filterwarnings('ignore')

# Import preprocessing
from .data_preprocessing import DataPreprocessor


class RosterOptimizationModel:
    """
    Machine learning model for predicting player performance.
    """
    
    def __init__(self):
        """Initialize the model."""
        self.model = None
        self.model_type = None
        self.preprocessor = DataPreprocessor()
        self.feature_names = None
        self.metrics = {}
        
    def load_and_prepare_data(self, filepath: str = '../../data/players_clean.csv'):
        """
        Load and prepare data for training.
        
        Args:
            filepath: Path to the dataset
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test, df_engineered)
        """
        print("Loading and preparing data...")
        
        # Load data
        df = self.preprocessor.load_data(filepath)
        
        # Preprocess
        df_engineered, X, y = self.preprocessor.preprocess(df, fit=True)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"✓ Training set: {X_train.shape[0]} samples")
        print(f"✓ Test set: {X_test.shape[0]} samples")
        
        return X_train, X_test, y_train, y_test, df_engineered
    
    def train_linear_regression(self, X_train, y_train, X_test, y_test):
        """
        Train Linear Regression model.
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            
        Returns:
            Tuple of (model, rmse, r2, mae)
        """
        print("\nTraining Linear Regression...")
        
        # Train model
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        
        # Predictions
        y_pred = lr_model.predict(X_test)
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Cross-validation score
        cv_scores = cross_val_score(lr_model, X_train, y_train, 
                                     cv=5, scoring='neg_mean_squared_error')
        cv_rmse = np.sqrt(-cv_scores.mean())
        
        print(f"  RMSE: {rmse:.4f}")
        print(f"  R²: {r2:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  CV RMSE: {cv_rmse:.4f}")
        
        return lr_model, rmse, r2, mae, cv_rmse
    
    def train_gradient_boosting(self, X_train, y_train, X_test, y_test):
        """
        Train Gradient Boosting model (CPU-friendly alternative to XGBoost).
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            
        Returns:
            Tuple of (model, rmse, r2, mae)
        """
        print("\nTraining Gradient Boosting (CPU-optimized)...")
        
        # Train model with CPU-friendly parameters
        gb_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=4,
            min_samples_split=5,
            min_samples_leaf=2,
            subsample=0.8,
            random_state=42,
            verbose=0
        )
        gb_model.fit(X_train, y_train)
        
        # Predictions
        y_pred = gb_model.predict(X_test)
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Cross-validation score
        cv_scores = cross_val_score(gb_model, X_train, y_train, 
                                     cv=5, scoring='neg_mean_squared_error')
        cv_rmse = np.sqrt(-cv_scores.mean())
        
        print(f"  RMSE: {rmse:.4f}")
        print(f"  R²: {r2:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  CV RMSE: {cv_rmse:.4f}")
        
        return gb_model, rmse, r2, mae, cv_rmse
    
    def train(self, filepath: str = '../../data/players_clean.csv'):
        """
        Train both models and select the best one based on RMSE.
        
        Args:
            filepath: Path to the dataset
        """
        print("=" * 70)
        print("Training ML Models for Player Performance Prediction")
        print("=" * 70)
        
        # Load and prepare data
        X_train, X_test, y_train, y_test, df_engineered = self.load_and_prepare_data(filepath)
        
        # Train Linear Regression
        lr_model, lr_rmse, lr_r2, lr_mae, lr_cv_rmse = self.train_linear_regression(
            X_train, y_train, X_test, y_test
        )
        
        # Train Gradient Boosting
        gb_model, gb_rmse, gb_r2, gb_mae, gb_cv_rmse = self.train_gradient_boosting(
            X_train, y_train, X_test, y_test
        )
        
        # Compare models and select best
        print("\n" + "=" * 70)
        print("Model Comparison")
        print("=" * 70)
        print(f"Linear Regression  - RMSE: {lr_rmse:.4f}, R²: {lr_r2:.4f}, CV RMSE: {lr_cv_rmse:.4f}")
        print(f"Gradient Boosting  - RMSE: {gb_rmse:.4f}, R²: {gb_r2:.4f}, CV RMSE: {gb_cv_rmse:.4f}")
        
        if gb_rmse < lr_rmse:
            self.model = gb_model
            self.model_type = 'GradientBoosting'
            best_rmse = gb_rmse
            best_r2 = gb_r2
            best_mae = gb_mae
            best_cv_rmse = gb_cv_rmse
            print(f"\n✓ Selected: Gradient Boosting (Lower RMSE)")
        else:
            self.model = lr_model
            self.model_type = 'LinearRegression'
            best_rmse = lr_rmse
            best_r2 = lr_r2
            best_mae = lr_mae
            best_cv_rmse = lr_cv_rmse
            print(f"\n✓ Selected: Linear Regression (Lower RMSE)")
        
        # Store metrics
        self.metrics = {
            'rmse': best_rmse,
            'r2': best_r2,
            'mae': best_mae,
            'cv_rmse': best_cv_rmse,
            'model_type': self.model_type
        }
        
        print("=" * 70)
        
        # Save model and preprocessor
        self.save_model()
        self.preprocessor.save_preprocessor('../models/preprocessor.pkl')
        
        return self.model, self.metrics
    
    def predict(self, df: pd.DataFrame = None, 
                filepath: str = '../../data/players_clean.csv'):
        """
        Make predictions on player data.
        
        Args:
            df: DataFrame to predict on (optional)
            filepath: Path to dataset if df not provided
            
        Returns:
            DataFrame with predictions and value index
        """
        print("=" * 70)
        print("Making Predictions")
        print("=" * 70)
        
        # Load model and preprocessor if not already loaded
        if self.model is None:
            self.load_model()
        
        if self.preprocessor.scaler is None:
            self.preprocessor.load_preprocessor('../models/preprocessor.pkl')
        
        # Load data if not provided
        if df is None:
            df = self.preprocessor.load_data(filepath)
        elif isinstance(df, str):
            # If df is actually a filepath string
            df = self.preprocessor.load_data(df)
        
        # Preprocess data
        df_engineered, X, _ = self.preprocessor.preprocess(df, fit=False)
        
        # Make predictions
        print("\nGenerating predictions...")
        predictions = self.model.predict(X)
        
        # Add predictions to dataframe
        df_engineered['predicted_performance'] = predictions
        
        # Calculate value index = predicted_performance / (salary_lakhs + 1)
        # Adding 1 to avoid division by zero
        df_engineered['value_index'] = (
            df_engineered['predicted_performance'] / 
            (df_engineered['salary_lakhs'] + 1)
        )
        
        print(f"✓ Predictions generated for {len(df_engineered)} players")
        
        # Save predictions with absolute path
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'players_with_predictions.csv')
        df_engineered.to_csv(output_path, index=False)
        print(f"✓ Predictions saved to {output_path}")
        
        # Display sample predictions
        print("\n" + "=" * 70)
        print("Sample Predictions")
        print("=" * 70)
        sample_cols = ['Player', 'Paying_Role', 'salary_lakhs', 
                       'performance_score', 'predicted_performance', 'value_index']
        print(df_engineered[sample_cols].head(10).to_string(index=False))
        
        # Display top value players
        print("\n" + "=" * 70)
        print("Top 10 Value Players (Best Value Index)")
        print("=" * 70)
        top_value = df_engineered.nlargest(10, 'value_index')
        print(top_value[sample_cols].to_string(index=False))
        
        print("\n✓ Prediction completed successfully!")
        print("=" * 70)
        
        return df_engineered
    
    def save_model(self, filepath: str = '../models/model.pkl'):
        """
        Save the trained model.
        
        Args:
            filepath: Path to save the model
        """
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model with metadata
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'metrics': self.metrics,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Model saved to {filepath}")
    
    def load_model(self, filepath: str = '../models/model.pkl'):
        """
        Load a trained model.
        
        Args:
            filepath: Path to the saved model
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found at {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.model_type = model_data['model_type']
        self.metrics = model_data.get('metrics', {})
        self.feature_names = model_data.get('feature_names', None)
        
        print(f"✓ Model loaded from {filepath}")
        print(f"  Model type: {self.model_type}")
        if self.metrics:
            print(f"  RMSE: {self.metrics.get('rmse', 'N/A'):.4f}")
            print(f"  R²: {self.metrics.get('r2', 'N/A'):.4f}")


def main():
    """
    Main CLI function.
    """
    parser = argparse.ArgumentParser(
        description='Apex Zero Roster Optimizer - ML Model Training and Prediction'
    )
    parser.add_argument(
        '--train',
        action='store_true',
        help='Train the model'
    )
    parser.add_argument(
        '--predict',
        action='store_true',
        help='Make predictions using trained model'
    )
    parser.add_argument(
        '--data',
        type=str,
        default='../../data/players_clean.csv',
        help='Path to the dataset (default: ../../data/players_clean.csv)'
    )
    
    args = parser.parse_args()
    
    # Initialize model
    model = RosterOptimizationModel()
    
    if args.train:
        # Train model
        model.train(filepath=args.data)
        
    elif args.predict:
        # Make predictions
        model.predict(filepath=args.data)
        
    else:
        # No arguments provided
        print("Usage:")
        print("  python ml_model.py --train         # Train and save model")
        print("  python ml_model.py --predict       # Load model and predict")
        print("  python ml_model.py --train --data path/to/data.csv")
        print("\nFor help: python ml_model.py --help")


if __name__ == "__main__":
    main()
