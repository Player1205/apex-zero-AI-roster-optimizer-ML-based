"""
Data Preprocessing Module for Apex Zero Roster Optimizer

This module handles:
- Loading raw dataset
- Applying feature engineering
- One-hot encoding categorical variables
- Scaling numeric features
- Saving processed dataset
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import pickle
import os
from typing import Tuple, Optional

# Import feature engineering functions
from .feature_engineering import engineer_features


class DataPreprocessor:
    """
    Data preprocessing pipeline for IPL player data.
    """
    
    def __init__(self):
        """Initialize the preprocessor with scalers and encoders."""
        self.scaler = None
        self.encoder = None
        self.feature_columns = None
        self.target_column = 'performance_score'
        
    def load_data(self, filepath: str = '../../data/players_clean.csv') -> pd.DataFrame:
        """
        Load the raw dataset.
        
        Args:
            filepath: Path to the CSV file
            
        Returns:
            DataFrame with raw data
        """
        try:
            df = pd.read_csv(filepath, encoding="latin1", sep=None, engine="python", on_bad_lines="skip")
            print(f"✓ Loaded dataset: {df.shape[0]} players, {df.shape[1]} columns")
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset not found at {filepath}")
        except Exception as e:
            raise Exception(f"Error loading dataset: {str(e)}")
    
    def apply_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply feature engineering to raw data.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        df_engineered = engineer_features(df)
        print(f"✓ Feature engineering complete: {df_engineered.shape[1]} total columns")
        return df_engineered
    
    def encode_categorical(self, df: pd.DataFrame, 
                          fit: bool = True) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        One-hot encode the Paying_Role column.
        
        Args:
            df: Input DataFrame
            fit: Whether to fit the encoder (True for training, False for inference)
            
        Returns:
            Tuple of (DataFrame with numeric features, one-hot encoded array)
        """
        if 'Paying_Role' not in df.columns:
            raise ValueError("Paying_Role column not found in DataFrame")
        
        # Extract the categorical column
        categorical_data = df[['Paying_Role']].copy()
        
        if fit:
            # Fit and transform
            self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            encoded = self.encoder.fit_transform(categorical_data)
            
            # Get feature names
            role_categories = self.encoder.get_feature_names_out(['Paying_Role'])
            print(f"✓ One-hot encoded Paying_Role: {len(role_categories)} categories")
        else:
            # Transform only
            if self.encoder is None:
                raise ValueError("Encoder not fitted. Call with fit=True first.")
            encoded = self.encoder.transform(categorical_data)
            role_categories = self.encoder.get_feature_names_out(['Paying_Role'])
        
        # Create DataFrame with encoded features
        encoded_df = pd.DataFrame(encoded, columns=role_categories, index=df.index)
        
        return encoded_df, encoded
    
    def scale_numeric_features(self, df: pd.DataFrame, 
                               fit: bool = True) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Scale numeric features using StandardScaler.
        
        Args:
            df: Input DataFrame
            fit: Whether to fit the scaler (True for training, False for inference)
            
        Returns:
            Tuple of (scaled DataFrame, scaled array)
        """
        # Define numeric columns to scale
        numeric_cols = [
            'AGE', 'Mat', 'Runs', 'Avg', 'SR', 
            'B_Inns', 'B_Wkts', 'B_Econ',
            'runs_per_match', 'wickets_per_match', 
            'batting_impact', 'bowling_impact',
            'salary_lakhs'
        ]
        
        # Filter columns that exist in the DataFrame
        numeric_cols = [col for col in numeric_cols if col in df.columns]
        
        if fit:
            # Fit and transform
            self.scaler = StandardScaler()
            scaled = self.scaler.fit_transform(df[numeric_cols])
            print(f"✓ Scaled {len(numeric_cols)} numeric features")
        else:
            # Transform only
            if self.scaler is None:
                raise ValueError("Scaler not fitted. Call with fit=True first.")
            scaled = self.scaler.transform(df[numeric_cols])
        
        # Create DataFrame with scaled features
        scaled_df = pd.DataFrame(scaled, columns=numeric_cols, index=df.index)
        
        # Store feature columns for later use
        self.feature_columns = numeric_cols
        
        return scaled_df, scaled
    
    def preprocess(self, df: pd.DataFrame, 
                   fit: bool = True) -> Tuple[pd.DataFrame, np.ndarray, pd.Series]:
        """
        Complete preprocessing pipeline.
        
        Steps:
        1. Apply feature engineering
        2. One-hot encode categorical features
        3. Scale numeric features
        4. Combine all features
        
        Args:
            df: Raw DataFrame
            fit: Whether to fit transformers (True for training, False for inference)
            
        Returns:
            Tuple of (processed DataFrame, feature matrix, target vector)
        """
        # Step 1: Feature engineering
        df_engineered = self.apply_feature_engineering(df)
        
        # Step 2: One-hot encode categorical features
        encoded_df, _ = self.encode_categorical(df_engineered, fit=fit)
        
        # Step 3: Scale numeric features
        scaled_df, _ = self.scale_numeric_features(df_engineered, fit=fit)
        
        # Step 4: Combine encoded and scaled features
        X = pd.concat([scaled_df, encoded_df], axis=1)
        
        # Extract target variable (performance_score)
        y = df_engineered[self.target_column] if self.target_column in df_engineered.columns else None
        
        print(f"✓ Preprocessing complete: {X.shape[1]} features")
        
        return df_engineered, X.values, y
    
    def save_preprocessor(self, filepath: str = '../models/preprocessor.pkl'):
        """
        Save the fitted preprocessor (scaler and encoder).
        
        Args:
            filepath: Path to save the preprocessor
        """
        if self.scaler is None or self.encoder is None:
            raise ValueError("Preprocessor not fitted. Run preprocess() with fit=True first.")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save both scaler and encoder
        preprocessor_data = {
            'scaler': self.scaler,
            'encoder': self.encoder,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(preprocessor_data, f)
        
        print(f"✓ Preprocessor saved to {filepath}")
    
    def load_preprocessor(self, filepath: str = '../models/preprocessor.pkl'):
        """
        Load a fitted preprocessor.
        
        Args:
            filepath: Path to the saved preprocessor
        """
        with open(filepath, 'rb') as f:
            preprocessor_data = pickle.load(f)
        
        self.scaler = preprocessor_data['scaler']
        self.encoder = preprocessor_data['encoder']
        self.feature_columns = preprocessor_data['feature_columns']
        self.target_column = preprocessor_data['target_column']
        
        print(f"✓ Preprocessor loaded from {filepath}")


def main():
    """
    Main function to run the preprocessing pipeline.
    """
    print("=" * 60)
    print("Apex Zero Roster Optimizer - Data Preprocessing")
    print("=" * 60)
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor()
    
    # Load raw data
    print("\n1. Loading dataset...")
    df = preprocessor.load_data('../../data/players_clean.csv')
    
    # Preprocess data
    print("\n2. Preprocessing data...")
    df_engineered, X, y = preprocessor.preprocess(df, fit=True)
    
    # Save preprocessor
    print("\n3. Saving preprocessor...")
    preprocessor.save_preprocessor('../models/preprocessor.pkl')
    
    # Save cleaned dataset with engineered features
    output_path = '../../data/players_preprocessed.csv'
    df_engineered.to_csv(output_path, index=False)
    print(f"✓ Preprocessed dataset saved to {output_path}")
    
    # Display summary
    print("\n" + "=" * 60)
    print("Preprocessing Summary")
    print("=" * 60)
    print(f"Total players: {df_engineered.shape[0]}")
    print(f"Total features (after encoding): {X.shape[1]}")
    print(f"Target variable: {preprocessor.target_column}")
    print(f"\nFeature columns ({len(preprocessor.feature_columns)}):")
    for col in preprocessor.feature_columns:
        print(f"  - {col}")
    
    print(f"\nRole categories ({len(preprocessor.encoder.categories_[0])}):")
    for role in preprocessor.encoder.categories_[0]:
        print(f"  - {role}")
    
    print("\n✓ Preprocessing pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
