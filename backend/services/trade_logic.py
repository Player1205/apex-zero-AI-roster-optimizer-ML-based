"""
Trade Logic Module for Apex Zero

This module provides trade analysis and recommendations:
- Identifies overpaid players (trade candidates)
- Identifies undervalued players (acquisition targets)
- Simulates trades
- Suggests contract extensions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class TradeAnalyzer:
    """
    Analyzes player value and provides trade recommendations.
    """
    
    def __init__(self):
        """Initialize the trade analyzer."""
        self.players_df = None
        
    def load_predictions(self, filepath: str = 'data/players_with_predictions.csv'):
        """
        Load player predictions data.
        
        Args:
            filepath: Path to predictions CSV
        """
        self.players_df = pd.read_csv(filepath)
        print(f"✓ Loaded {len(self.players_df)} players with predictions")
        
    def identify_overpaid(
        self,
        top_n: int = 10,
        min_salary: float = 100
    ) -> pd.DataFrame:
        """
        Identify overpaid players (trade candidates).
        
        Players with low value_index relative to their salary are overpaid.
        
        Args:
            top_n: Number of overpaid players to return
            min_salary: Minimum salary threshold (lakhs)
            
        Returns:
            DataFrame of overpaid players
        """
        if self.players_df is None:
            raise ValueError("No player data loaded. Call load_predictions() first.")
        
        # Filter by minimum salary
        filtered = self.players_df[self.players_df['salary_lakhs'] >= min_salary].copy()
        
        # Sort by value_index (ascending - lowest value first)
        overpaid = filtered.nsmallest(top_n, 'value_index')
        
        # Add trade recommendation reason
        overpaid['trade_reason'] = overpaid.apply(
            lambda x: f"Low value: {x['value_index']:.4f} (Salary: {x['salary_lakhs']:.0f}L, Performance: {x['predicted_performance']:.2f})",
            axis=1
        )
        
        return overpaid
    
    def identify_undervalued(
        self,
        top_n: int = 10,
        max_salary: float = 1000
    ) -> pd.DataFrame:
        """
        Identify undervalued players (acquisition targets).
        
        Players with high value_index are undervalued and good acquisition targets.
        
        Args:
            top_n: Number of undervalued players to return
            max_salary: Maximum salary threshold (lakhs)
            
        Returns:
            DataFrame of undervalued players
        """
        if self.players_df is None:
            raise ValueError("No player data loaded. Call load_predictions() first.")
        
        # Filter by maximum salary
        filtered = self.players_df[self.players_df['salary_lakhs'] <= max_salary].copy()
        
        # Sort by value_index (descending - highest value first)
        undervalued = filtered.nlargest(top_n, 'value_index')
        
        # Add acquisition recommendation reason
        undervalued['acquisition_reason'] = undervalued.apply(
            lambda x: f"High value: {x['value_index']:.4f} (Salary: {x['salary_lakhs']:.0f}L, Performance: {x['predicted_performance']:.2f})",
            axis=1
        )
        
        return undervalued
    
    def simulate_trade(
        self,
        trade_out_player: str,
        trade_in_player: str
    ) -> Dict:
        """
        Simulate a trade between two players.
        
        Args:
            trade_out_player: Player name to trade away
            trade_in_player: Player name to acquire
            
        Returns:
            Dict with trade simulation results
        """
        if self.players_df is None:
            raise ValueError("No player data loaded. Call load_predictions() first.")
        
        # Find players
        out_df = self.players_df[self.players_df['Player'] == trade_out_player]
        in_df = self.players_df[self.players_df['Player'] == trade_in_player]

        if out_df.empty or in_df.empty:
            raise ValueError("Player not found")

        out_player = out_df.iloc[0].to_dict()
        in_player = in_df.iloc[0].to_dict()
        
        out_player = {k: (0 if pd.isna(v) else v) for k, v in out_player.items()}
        in_player = {k: (0 if pd.isna(v) else v) for k, v in in_player.items()}
        
        # Calculate trade impact
        result = {
            'trade_out': {
                'player': trade_out_player,
                'role': out_player['Paying_Role'],
                'salary': float(out_player['salary_lakhs']),
                'performance': float(out_player['predicted_performance']),
                'value_index': float(out_player['value_index'])
            },
            'trade_in': {
                'player': trade_in_player,
                'role': in_player['Paying_Role'],
                'salary': float(in_player['salary_lakhs']),
                'performance': float(in_player['predicted_performance']),
                'value_index': float(in_player['value_index'])
            },
            'impact': {
                'salary_change': float(in_player['salary_lakhs'] - out_player['salary_lakhs']),
                'performance_change': float(in_player['predicted_performance'] - out_player['predicted_performance']),
                'value_index_change': float(in_player['value_index'] - out_player['value_index'])
            }
        }
        
        # Recommendation
        if result['impact']['performance_change'] > 0 and result['impact']['salary_change'] <= 0:
            result['recommendation'] = "Highly Recommended ✓✓✓"
        elif result['impact']['performance_change'] > 0:
            result['recommendation'] = "Recommended ✓✓"
        elif result['impact']['value_index_change'] > 0:
            result['recommendation'] = "Consider ✓"
        else:
            result['recommendation'] = "Not Recommended ✗"
        
        return result
    
    def suggest_contract_extensions(
        self,
        top_n: int = 10,
        min_value_index: float = 0.3,
        max_salary: float = 800
    ) -> pd.DataFrame:
        """
        Suggest players for contract extensions.
        
        Players with high value_index and reasonable salary are good extension candidates.
        
        Args:
            top_n: Number of extension candidates to return
            min_value_index: Minimum value_index threshold
            max_salary: Maximum salary threshold (lakhs)
            
        Returns:
            DataFrame of contract extension candidates
        """
        if self.players_df is None:
            raise ValueError("No player data loaded. Call load_predictions() first.")
        
        # Filter candidates
        filtered = self.players_df[
            (self.players_df['value_index'] >= min_value_index) &
            (self.players_df['salary_lakhs'] <= max_salary)
        ].copy()
        
        # Sort by value_index (descending)
        extensions = filtered.nlargest(top_n, 'value_index')
        
        # Add extension reason
        extensions['extension_reason'] = extensions.apply(
            lambda x: f"Strong value: {x['value_index']:.4f} (Performance: {x['predicted_performance']:.2f}, Salary: {x['salary_lakhs']:.0f}L)",
            axis=1
        )
        
        # Suggest contract value increase
        extensions['suggested_salary'] = extensions.apply(
            lambda x: min(x['salary_lakhs'] * 1.2, max_salary),  # 20% increase, capped
            axis=1
        )
        
        return extensions
    
    def analyze_team_composition(
        self,
        team_name: Optional[str] = None
    ) -> Dict:
        """
        Analyze team composition and identify issues.
        
        Args:
            team_name: Specific team to analyze (optional)
            
        Returns:
            Dict with team analysis
        """
        if self.players_df is None:
            raise ValueError("No player data loaded. Call load_predictions() first.")
        
        if team_name:
            team_df = self.players_df[self.players_df['TEAM'] == team_name].copy()
        else:
            team_df = self.players_df.copy()
        
        analysis = {
            'total_players': len(team_df),
            'total_salary': float(team_df['salary_lakhs'].sum()),
            'avg_salary': float(team_df['salary_lakhs'].mean()),
            'total_performance': float(team_df['predicted_performance'].sum()),
            'avg_performance': float(team_df['predicted_performance'].mean()),
            'avg_value_index': float(team_df['value_index'].mean()),
            'role_distribution': team_df['Paying_Role'].value_counts().to_dict(),
            'salary_distribution': {
                'top_earners_pct': float((team_df.nlargest(5, 'salary_lakhs')['salary_lakhs'].sum() / 
                                         team_df['salary_lakhs'].sum()) * 100),
                'bottom_earners_pct': float((team_df.nsmallest(5, 'salary_lakhs')['salary_lakhs'].sum() / 
                                            team_df['salary_lakhs'].sum()) * 100)
            }
        }
        
        # Identify issues
        issues = []
        
        # Check for overpaid players
        overpaid_count = len(team_df[team_df['value_index'] < 0.05])
        if overpaid_count > 0:
            issues.append(f"{overpaid_count} overpaid players (value_index < 0.05)")
        
        # Check role balance
        role_dist = analysis['role_distribution']
        if role_dist.get('Batsman', 0) < 5:
            issues.append(f"Insufficient batsmen ({role_dist.get('Batsman', 0)})")
        if role_dist.get('Bowler', 0) < 5:
            issues.append(f"Insufficient bowlers ({role_dist.get('Bowler', 0)})")
        if role_dist.get('Wicketkeeper', 0) < 1:
            issues.append("No wicketkeeper")
        
        analysis['issues'] = issues
        
        return analysis
    
    def get_trade_candidates_summary(self) -> Dict:
        """
        Get comprehensive trade recommendations summary.
        
        Returns:
            Dict with all trade recommendations
        """
        return {
            'overpaid_players': self.identify_overpaid(top_n=10).to_dict('records'),
            'undervalued_players': self.identify_undervalued(top_n=10).to_dict('records'),
            'contract_extensions': self.suggest_contract_extensions(top_n=10).to_dict('records')
        }


class ValueIndexAnalyzer:
    """
    Analyzes value index distribution and trends.
    """
    
    @staticmethod
    def categorize_players(players_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Categorize players by value index.
        
        Categories:
        - Elite value (>0.5): Exceptional value for money
        - Good value (0.3-0.5): Strong performers for salary
        - Fair value (0.1-0.3): Adequate performance
        - Poor value (0.05-0.1): Underperforming for salary
        - Overpaid (<0.05): Significantly overpaid
        
        Args:
            players_df: DataFrame with value_index
            
        Returns:
            Dict mapping category to DataFrame
        """
        categories = {
            'elite_value': players_df[players_df['value_index'] > 0.5].copy(),
            'good_value': players_df[
                (players_df['value_index'] > 0.3) & 
                (players_df['value_index'] <= 0.5)
            ].copy(),
            'fair_value': players_df[
                (players_df['value_index'] > 0.1) & 
                (players_df['value_index'] <= 0.3)
            ].copy(),
            'poor_value': players_df[
                (players_df['value_index'] > 0.05) & 
                (players_df['value_index'] <= 0.1)
            ].copy(),
            'overpaid': players_df[players_df['value_index'] <= 0.05].copy()
        }
        
        # Add category column
        for category, df in categories.items():
            df['value_category'] = category
        
        return categories
    
    @staticmethod
    def get_value_distribution(players_df: pd.DataFrame) -> Dict:
        """
        Get distribution statistics of value index.
        
        Args:
            players_df: DataFrame with value_index
            
        Returns:
            Dict with distribution statistics
        """
        categories = ValueIndexAnalyzer.categorize_players(players_df)
        
        return {
            'total_players': len(players_df),
            'category_counts': {
                category: len(df) for category, df in categories.items()
            },
            'category_percentages': {
                category: (len(df) / len(players_df)) * 100 
                for category, df in categories.items()
            },
            'statistics': {
                'mean': float(players_df['value_index'].mean()),
                'median': float(players_df['value_index'].median()),
                'std': float(players_df['value_index'].std()),
                'min': float(players_df['value_index'].min()),
                'max': float(players_df['value_index'].max())
            }
        }


if __name__ == "__main__":
    # Test the trade analyzer
    print("Testing Trade Analyzer...")
    
    try:
        analyzer = TradeAnalyzer()
        analyzer.load_predictions('../../data/players_with_predictions.csv')
        
        print("\n1. Top 5 Overpaid Players (Trade Candidates):")
        overpaid = analyzer.identify_overpaid(top_n=5)
        print(overpaid[['Player', 'salary_lakhs', 'predicted_performance', 'value_index']].to_string(index=False))
        
        print("\n2. Top 5 Undervalued Players (Acquisition Targets):")
        undervalued = analyzer.identify_undervalued(top_n=5)
        print(undervalued[['Player', 'salary_lakhs', 'predicted_performance', 'value_index']].to_string(index=False))
        
        print("\n3. Top 5 Contract Extension Candidates:")
        extensions = analyzer.suggest_contract_extensions(top_n=5)
        print(extensions[['Player', 'salary_lakhs', 'suggested_salary', 'value_index']].to_string(index=False))
        
        print("\n✓ Trade analyzer test completed successfully!")
        
    except FileNotFoundError:
        print("⚠️  Prediction file not found. Run ml_model.py --predict first.")
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
