"""
Utility Helper Functions for Apex Zero

Provides common utility functions used across the application.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
from datetime import datetime


def ensure_directory_exists(filepath: str) -> None:
    """
    Ensure the directory for a filepath exists.
    
    Args:
        filepath: Path to file
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def load_csv_safe(filepath: str) -> pd.DataFrame:
    """
    Safely load CSV file with error handling.
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        DataFrame
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or invalid
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            raise ValueError(f"File is empty: {filepath}")
        return df
    except pd.errors.EmptyDataError:
        raise ValueError(f"File is empty: {filepath}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")


def save_csv_safe(df: pd.DataFrame, filepath: str) -> None:
    """
    Safely save DataFrame to CSV.
    
    Args:
        df: DataFrame to save
        filepath: Destination path
    """
    ensure_directory_exists(filepath)
    df.to_csv(filepath, index=False)


def validate_player_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate that DataFrame has required player columns.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If validation fails
    """
    required_columns = [
        'Player', 'TEAM', 'AGE', 'Paying_Role', 'Mat', 'Runs', 
        'Avg', 'SR', 'B_Inns', 'B_Wkts', 'B_Econ', 'salary_lakhs'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    return True


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted string
    """
    if currency == "INR":
        # Indian numbering system (lakhs, crores)
        if amount >= 100:
            crores = amount / 100
            return f"₹{crores:.2f} Cr"
        else:
            return f"₹{amount:.2f} L"
    else:
        return f"{currency} {amount:,.2f}"


def calculate_percentile(value: float, series: pd.Series) -> float:
    """
    Calculate percentile rank of a value in a series.
    
    Args:
        value: Value to rank
        series: Series to compare against
        
    Returns:
        Percentile (0-100)
    """
    return (series <= value).sum() / len(series) * 100


def get_role_emoji(role: str) -> str:
    """
    Get emoji for player role.
    
    Args:
        role: Player role
        
    Returns:
        Emoji string
    """
    emoji_map = {
        'Batsman': '🏏',
        'Bowler': '🎾',
        'Allrounder': '⭐',
        'Wicketkeeper': '🧤'
    }
    return emoji_map.get(role, '👤')


def get_value_rating(value_index: float) -> str:
    """
    Get value rating description for value_index.
    
    Args:
        value_index: Value index score
        
    Returns:
        Rating description
    """
    if value_index > 0.5:
        return "Elite Value 🔥"
    elif value_index > 0.3:
        return "Good Value ⭐"
    elif value_index > 0.1:
        return "Fair Value ✓"
    elif value_index > 0.05:
        return "Poor Value ⚠️"
    else:
        return "Overpaid ⛔"


def create_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Create summary statistics for player DataFrame.
    
    Args:
        df: Player DataFrame
        
    Returns:
        Dict with summary stats
    """
    stats = {
        'total_players': len(df),
        'total_teams': df['TEAM'].nunique() if 'TEAM' in df.columns else 0,
        'avg_age': float(df['AGE'].mean()) if 'AGE' in df.columns else 0,
        'total_salary': float(df['salary_lakhs'].sum()) if 'salary_lakhs' in df.columns else 0,
        'avg_salary': float(df['salary_lakhs'].mean()) if 'salary_lakhs' in df.columns else 0,
        'salary_std': float(df['salary_lakhs'].std()) if 'salary_lakhs' in df.columns else 0
    }
    
    if 'predicted_performance' in df.columns:
        stats['avg_performance'] = float(df['predicted_performance'].mean())
        stats['total_performance'] = float(df['predicted_performance'].sum())
    
    if 'value_index' in df.columns:
        stats['avg_value_index'] = float(df['value_index'].mean())
        stats['median_value_index'] = float(df['value_index'].median())
    
    if 'Paying_Role' in df.columns:
        stats['role_distribution'] = df['Paying_Role'].value_counts().to_dict()
    
    return stats


def filter_players_by_criteria(
    df: pd.DataFrame,
    min_salary: Optional[float] = None,
    max_salary: Optional[float] = None,
    roles: Optional[List[str]] = None,
    teams: Optional[List[str]] = None,
    min_value_index: Optional[float] = None,
    max_age: Optional[int] = None
) -> pd.DataFrame:
    """
    Filter players by multiple criteria.
    
    Args:
        df: Player DataFrame
        min_salary: Minimum salary filter
        max_salary: Maximum salary filter
        roles: List of roles to include
        teams: List of teams to include
        min_value_index: Minimum value index
        max_age: Maximum age
        
    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()
    
    if min_salary is not None:
        filtered = filtered[filtered['salary_lakhs'] >= min_salary]
    
    if max_salary is not None:
        filtered = filtered[filtered['salary_lakhs'] <= max_salary]
    
    if roles is not None:
        filtered = filtered[filtered['Paying_Role'].isin(roles)]
    
    if teams is not None:
        filtered = filtered[filtered['TEAM'].isin(teams)]
    
    if min_value_index is not None and 'value_index' in filtered.columns:
        filtered = filtered[filtered['value_index'] >= min_value_index]
    
    if max_age is not None:
        filtered = filtered[filtered['AGE'] <= max_age]
    
    return filtered


def export_to_json(data: Dict, filepath: str, indent: int = 2) -> None:
    """
    Export data to JSON file.
    
    Args:
        data: Data to export
        filepath: Destination path
        indent: JSON indentation
    """
    ensure_directory_exists(filepath)
    
    # Convert numpy types to native Python types
    def convert_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        return obj
    
    # Recursively convert types
    def recursive_convert(data):
        if isinstance(data, dict):
            return {k: recursive_convert(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [recursive_convert(item) for item in data]
        else:
            return convert_types(data)
    
    converted_data = recursive_convert(data)
    
    with open(filepath, 'w') as f:
        json.dump(converted_data, f, indent=indent)


def generate_timestamp() -> str:
    """
    Generate timestamp string.
    
    Returns:
        Timestamp string (YYYY-MM-DD_HH-MM-SS)
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def check_model_exists(model_path: str = 'backend/models/model.pkl') -> bool:
    """
    Check if trained model exists.
    
    Args:
        model_path: Path to model file
        
    Returns:
        True if model exists
    """
    return os.path.exists(model_path)


def check_predictions_exist(predictions_path: str = 'data/players_with_predictions.csv') -> bool:
    """
    Check if predictions file exists.
    
    Args:
        predictions_path: Path to predictions file
        
    Returns:
        True if predictions exist
    """
    return os.path.exists(predictions_path)


def get_top_n_players(
    df: pd.DataFrame,
    column: str,
    n: int = 10,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Get top N players by specified column.
    
    Args:
        df: Player DataFrame
        column: Column to sort by
        n: Number of players to return
        ascending: Sort order
        
    Returns:
        DataFrame with top N players
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    return df.nlargest(n, column) if not ascending else df.nsmallest(n, column)


def calculate_team_chemistry(players: List[Dict]) -> float:
    """
    Calculate team chemistry score (placeholder for future implementation).
    
    Args:
        players: List of player dictionaries
        
    Returns:
        Chemistry score (0-100)
    """
    # Placeholder implementation
    # In real system, this would consider:
    # - Players from same team (synergy bonus)
    # - Age distribution (experience + youth balance)
    # - Role complementarity
    
    if not players:
        return 0.0
    
    # Simple implementation: reward diverse roles
    roles = [p.get('Paying_Role') for p in players if 'Paying_Role' in p]
    unique_roles = len(set(roles))
    
    # Basic chemistry score
    chemistry = (unique_roles / 4) * 100  # 4 possible roles
    
    return min(chemistry, 100.0)


class DataValidator:
    """Validator for API data."""
    
    @staticmethod
    def validate_salary_cap(salary_cap: float) -> bool:
        """Validate salary cap value."""
        if salary_cap <= 0:
            raise ValueError("Salary cap must be positive")
        if salary_cap > 100000:  # 1000 crores
            raise ValueError("Salary cap too high (max 100,000 lakhs)")
        return True
    
    @staticmethod
    def validate_roster_size(roster_size: int) -> bool:
        """Validate roster size."""
        if roster_size < 11:
            raise ValueError("Roster size must be at least 11 players")
        if roster_size > 30:
            raise ValueError("Roster size cannot exceed 30 players")
        return True
    
    @staticmethod
    def validate_role_constraints(constraints: Dict) -> bool:
        """Validate role constraints."""
        valid_roles = {'Batsman', 'Bowler', 'Allrounder', 'Wicketkeeper'}
        
        for role, (min_count, max_count) in constraints.items():
            if role not in valid_roles:
                raise ValueError(f"Invalid role: {role}")
            if min_count < 0:
                raise ValueError(f"Minimum count for {role} cannot be negative")
            if max_count < min_count:
                raise ValueError(f"Maximum count for {role} must be >= minimum count")
        
        return True


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")
    
    # Test currency formatting
    print(f"Currency format: {format_currency(1500)}")
    print(f"Currency format: {format_currency(50)}")
    
    # Test role emoji
    print(f"Batsman emoji: {get_role_emoji('Batsman')}")
    
    # Test value rating
    print(f"Value rating (0.8): {get_value_rating(0.8)}")
    print(f"Value rating (0.02): {get_value_rating(0.02)}")
    
    print("\n✓ Utility functions test completed!")
