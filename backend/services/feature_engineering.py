"""
Feature Engineering Module for Apex Zero Roster Optimizer

This module computes advanced performance metrics for IPL players including:
- Runs per match
- Wickets per match
- Batting impact
- Bowling impact
- Overall performance score
"""

import pandas as pd
import numpy as np
from typing import Optional


def compute_performance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute advanced performance metrics for players.
    
    Metrics computed:
    - runs_per_match: Average runs scored per match
    - wickets_per_match: Average wickets taken per innings bowled
    - batting_impact: Runs per match adjusted by strike rate
    - bowling_impact: Wickets per match adjusted by economy rate
    - performance_score: Weighted combination of batting and bowling impact
    
    Args:
        df: DataFrame with player statistics
        
    Returns:
        DataFrame with additional performance metric columns
    """
    df = df.copy()
    
    # Runs per match - handles division by zero
    df['runs_per_match'] = df['Runs'] / df['Mat'].apply(lambda x: max(1, x))
    
    # Wickets per match - handles division by zero
    df['wickets_per_match'] = df['B_Wkts'] / df['B_Inns'].apply(lambda x: max(1, x))
    
    # Batting impact - strike rate adjusted runs
    df['batting_impact'] = df['runs_per_match'] * (df['SR'] / 100)
    
    # Bowling impact - economy-adjusted wickets (lower economy is better)
    df['bowling_impact'] = df['wickets_per_match'] / df['B_Econ'].apply(lambda x: max(0.1, x))
    
    # Overall performance score - weighted combination
    # 50% runs per match, 30% batting impact, 20% bowling impact
    df['performance_score'] = (
        0.5 * df['runs_per_match'] + 
        0.3 * df['batting_impact'] + 
        0.2 * df['bowling_impact']
    )
    
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Strategy:
    - Numeric columns: Fill with 0 (for stats like wickets, runs)
    - Categorical columns: Fill with 'Unknown'
    - Bowling stats: Fill with 0 for batsmen
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with missing values handled
    """
    df = df.copy()
    
    # Fill missing numeric bowling stats with 0 (many batsmen don't bowl)
    bowling_cols = ['B_Inns', 'B_Wkts', 'B_Econ']
    for col in bowling_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # Fill missing batting stats with 0
    batting_cols = ['Runs', 'Avg', 'SR']
    for col in batting_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # Fill missing Mat with 1 (to avoid division by zero)
    if 'Mat' in df.columns:
        df['Mat'] = df['Mat'].fillna(1)
    
    # Fill missing salary with median
    if 'salary_lakhs' in df.columns:
        median_salary = df['salary_lakhs'].median()
        df['salary_lakhs'] = df['salary_lakhs'].fillna(median_salary)
    
    # Fill categorical columns
    if 'Paying_Role' in df.columns:
        df['Paying_Role'] = df['Paying_Role'].fillna('Unknown')
    
    if 'TEAM' in df.columns:
        df['TEAM'] = df['TEAM'].fillna('Unknown')
    
    if 'Player' in df.columns:
        df['Player'] = df['Player'].fillna('Unknown Player')
    
    return df


def normalize_paying_role(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the Paying_Role column to standard categories.
    
    Standardizes variations like:
    - 'Allrounder' / 'All-rounder' / 'ALL ROUNDER' -> 'Allrounder'
    - 'WK' / 'Wicketkeeper' / 'Keeper' -> 'Wicketkeeper'
    - 'Bowler' / 'BOWLER' -> 'Bowler'
    - 'Batsman' / 'BATSMAN' / 'Batter' -> 'Batsman'
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with normalized Paying_Role
    """
    df = df.copy()
    
    if 'Paying_Role' not in df.columns:
        return df
    
    # Create a mapping for standardization
    role_mapping = {
        'allrounder': 'Allrounder',
        'all-rounder': 'Allrounder',
        'all rounder': 'Allrounder',
        'wicketkeeper': 'Wicketkeeper',
        'wk': 'Wicketkeeper',
        'keeper': 'Wicketkeeper',
        'wicket-keeper': 'Wicketkeeper',
        'bowler': 'Bowler',
        'batsman': 'Batsman',
        'batter': 'Batsman',
        'batting': 'Batsman',
        'unknown': 'Unknown'
    }
    
    # Normalize by converting to lowercase and mapping
    df['Paying_Role'] = df['Paying_Role'].str.lower().str.strip()
    df['Paying_Role'] = df['Paying_Role'].map(role_mapping).fillna(df['Paying_Role'])
    
    # Capitalize first letter for consistency
    df['Paying_Role'] = df['Paying_Role'].str.capitalize()
    
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Complete feature engineering pipeline.
    
    Performs the following operations:
    1. Handle missing values
    2. Normalize Paying_Role
    3. Compute performance metrics
    
    Args:
        df: Raw player DataFrame
        
    Returns:
        DataFrame with engineered features
    """
    # Step 1: Handle missing values
    df = handle_missing_values(df)
    
    # Step 2: Normalize paying role
    df = normalize_paying_role(df)
    
    # Step 3: Compute performance metrics
    df = compute_performance_metrics(df)
    
    return df


def get_feature_names() -> list:
    """
    Get the list of engineered feature names.
    
    Returns:
        List of feature column names
    """
    return [
        'runs_per_match',
        'wickets_per_match',
        'batting_impact',
        'bowling_impact',
        'performance_score'
    ]


if __name__ == "__main__":
    # Test the feature engineering pipeline
    print("Testing Feature Engineering Module...")
    
    # Load sample data
    df = pd.read_csv('../../data/players_clean.csv')
    print(f"\nOriginal shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Apply feature engineering
    df_engineered = engineer_features(df)
    print(f"\nEngineered shape: {df_engineered.shape}")
    print(f"New columns: {get_feature_names()}")
    
    # Display sample results
    print("\nSample engineered features:")
    cols_to_show = ['Player', 'Paying_Role', 'runs_per_match', 
                    'batting_impact', 'bowling_impact', 'performance_score']
    print(df_engineered[cols_to_show].head(10))
    
    # Show statistics
    print("\nPerformance Score Statistics:")
    print(df_engineered['performance_score'].describe())
