"""
Roster Optimizer Module for Apex Zero

This module implements roster optimization using Mixed Integer Linear Programming (MILP)
with PuLP. It maximizes team performance under salary cap and role constraints.

Features:
- MILP optimization using PuLP
- Salary cap constraint
- Roster size constraint
- Role-based constraints (min/max players per role)
- Greedy fallback algorithm
"""

import pandas as pd
import numpy as np
from pulp import *
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class RosterOptimizer:
    """
    Optimizes roster selection using MILP to maximize performance under constraints.
    """
    
    def __init__(self):
        """Initialize the optimizer."""
        self.problem = None
        self.decision_vars = None
        self.solution = None
        
    def optimize_roster(
        self,
        players_df: pd.DataFrame,
        salary_cap: float,
        roster_size: int = 25,
        role_constraints: Optional[Dict[str, Tuple[int, int]]] = None,
        solver_time_limit: int = 60
    ) -> Dict:
        """
        Optimize roster selection using MILP.
        
        Args:
            players_df: DataFrame with player data including predicted_performance and salary
            salary_cap: Maximum total salary allowed (in lakhs)
            roster_size: Number of players to select
            role_constraints: Dict mapping role to (min, max) players
                             e.g., {'Batsman': (6, 10), 'Bowler': (6, 10)}
            solver_time_limit: Maximum solver time in seconds
            
        Returns:
            Dict with optimization results
        """
        print("=" * 70)
        print("Roster Optimization - MILP Approach")
        print("=" * 70)
        
        # Validate input
        if 'predicted_performance' not in players_df.columns:
            raise ValueError("DataFrame must contain 'predicted_performance' column")
        if 'salary_lakhs' not in players_df.columns:
            raise ValueError("DataFrame must contain 'salary_lakhs' column")
        
        # Set default role constraints if not provided
        if role_constraints is None:
            role_constraints = {
                'Batsman': (5, 10),
                'Bowler': (5, 10),
                'Allrounder': (2, 6),
                'Wicketkeeper': (1, 3)
            }
        
        print(f"\nConstraints:")
        print(f"  Salary Cap: {salary_cap:,.0f} lakhs")
        print(f"  Roster Size: {roster_size} players")
        print(f"  Role Constraints:")
        for role, (min_val, max_val) in role_constraints.items():
            print(f"    {role}: {min_val}-{max_val} players")
        
        # Prepare data
        players_df = players_df.copy()
        players_df['player_id'] = range(len(players_df))
        
        n_players = len(players_df)
        player_ids = players_df['player_id'].tolist()
        
        # Extract data
        performance = players_df.set_index('player_id')['predicted_performance'].to_dict()
        salary = players_df.set_index('player_id')['salary_lakhs'].to_dict()
        role = players_df.set_index('player_id')['Paying_Role'].to_dict()
        
        print(f"\n✓ Loaded {n_players} players")
        
        # Create MILP problem
        print("\nBuilding MILP model...")
        self.problem = LpProblem("Roster_Optimization", LpMaximize)
        
        # Decision variables: x[i] = 1 if player i is selected, 0 otherwise
        self.decision_vars = LpVariable.dicts(
            "player",
            player_ids,
            cat='Binary'
        )
        
        # Objective: Maximize total predicted performance
        self.problem += (
            lpSum([self.decision_vars[i] * performance[i] for i in player_ids]),
            "Total_Performance"
        )
        
        # Constraint 1: Salary cap
        self.problem += (
            lpSum([self.decision_vars[i] * salary[i] for i in player_ids]) <= salary_cap,
            "Salary_Cap"
        )
        
        # Constraint 2: Roster size
        self.problem += (
            lpSum([self.decision_vars[i] for i in player_ids]) == roster_size,
            "Roster_Size"
        )
        
        # Constraint 3: Role constraints
        for role_name, (min_count, max_count) in role_constraints.items():
            role_players = [i for i in player_ids if role[i] == role_name]
            if role_players:
                # Minimum constraint
                self.problem += (
                    lpSum([self.decision_vars[i] for i in role_players]) >= min_count,
                    f"Min_{role_name}"
                )
                # Maximum constraint
                self.problem += (
                    lpSum([self.decision_vars[i] for i in role_players]) <= max_count,
                    f"Max_{role_name}"
                )
        
        print("✓ MILP model built")
        
        # Solve
        print("\nSolving MILP problem...")
        try:
            # Use CBC solver (default, open-source)
            solver = PULP_CBC_CMD(msg=0, timeLimit=solver_time_limit)
            self.problem.solve(solver)
            
            status = LpStatus[self.problem.status]
            print(f"✓ Solution status: {status}")
            
            if status == 'Optimal':
                return self._extract_solution(players_df, salary_cap, roster_size, role_constraints)
            else:
                print(f"⚠️  MILP did not find optimal solution. Trying greedy fallback...")
                return self.greedy_optimize(players_df, salary_cap, roster_size, role_constraints)
                
        except Exception as e:
            print(f"⚠️  MILP solver failed: {str(e)}")
            print("Falling back to greedy algorithm...")
            return self.greedy_optimize(players_df, salary_cap, roster_size, role_constraints)
    
    def _extract_solution(
        self,
        players_df: pd.DataFrame,
        salary_cap: float,
        roster_size: int,
        role_constraints: Dict[str, Tuple[int, int]]
    ) -> Dict:
        """
        Extract solution from solved MILP problem.
        
        Args:
            players_df: Original player DataFrame
            salary_cap: Salary cap constraint
            roster_size: Roster size constraint
            role_constraints: Role constraints
            
        Returns:
            Dict with solution details
        """
        # Get selected players
        selected_ids = [
            i for i in self.decision_vars 
            if self.decision_vars[i].varValue == 1
        ]
        
        selected_players = players_df[
            players_df['player_id'].isin(selected_ids)
        ].copy()
        
        # Calculate statistics
        total_performance = selected_players['predicted_performance'].sum()
        total_salary = selected_players['salary_lakhs'].sum()
        avg_value_index = selected_players['value_index'].mean()
        
        # Role distribution
        role_distribution = selected_players['Paying_Role'].value_counts().to_dict()
        
        # Create result
        result = {
            'status': 'Optimal',
            'method': 'MILP',
            'selected_players': selected_players.to_dict('records'),
            'total_players': len(selected_players),
            'total_performance': float(total_performance),
            'total_salary': float(total_salary),
            'salary_remaining': float(salary_cap - total_salary),
            'avg_value_index': float(avg_value_index),
            'role_distribution': role_distribution,
            'constraints_met': True
        }
        
        # Display results
        print("\n" + "=" * 70)
        print("Optimization Results (MILP)")
        print("=" * 70)
        print(f"Total Players Selected: {result['total_players']}")
        print(f"Total Performance: {result['total_performance']:.2f}")
        print(f"Total Salary: {result['total_salary']:,.0f} lakhs")
        print(f"Salary Remaining: {result['salary_remaining']:,.0f} lakhs")
        print(f"Average Value Index: {result['avg_value_index']:.4f}")
        print(f"\nRole Distribution:")
        for role, count in role_distribution.items():
            print(f"  {role}: {count} players")
        
        return result
    
    def greedy_optimize(
        self,
        players_df: pd.DataFrame,
        salary_cap: float,
        roster_size: int,
        role_constraints: Optional[Dict[str, Tuple[int, int]]] = None
    ) -> Dict:
        """
        Greedy fallback optimization algorithm.
        
        Selects players in order of value_index (descending) while respecting constraints.
        
        Args:
            players_df: DataFrame with player data
            salary_cap: Maximum total salary
            roster_size: Number of players to select
            role_constraints: Role constraints
            
        Returns:
            Dict with optimization results
        """
        print("=" * 70)
        print("Roster Optimization - Greedy Approach")
        print("=" * 70)
        
        if role_constraints is None:
            role_constraints = {
                'Batsman': (5, 10),
                'Bowler': (5, 10),
                'Allrounder': (2, 6),
                'Wicketkeeper': (1, 3)
            }
        
        # Sort by value_index (descending)
        sorted_players = players_df.sort_values('value_index', ascending=False).copy()
        
        selected = []
        total_salary = 0
        role_counts = {role: 0 for role in role_constraints.keys()}
        
        print(f"\nSelecting players greedily by value_index...")
        
        for idx, player in sorted_players.iterrows():
            # Check if we've reached roster size
            if len(selected) >= roster_size:
                break
            
            player_role = player['Paying_Role']
            player_salary = player['salary_lakhs']
            
            # Check salary constraint
            if total_salary + player_salary > salary_cap:
                continue
            
            # Check role constraints
            if player_role in role_constraints:
                min_count, max_count = role_constraints[player_role]
                current_count = role_counts.get(player_role, 0)
                
                # Check if we can still add this role
                if current_count >= max_count:
                    continue
            
            # Add player
            selected.append(player)
            total_salary += player_salary
            role_counts[player_role] = role_counts.get(player_role, 0) + 1
        
        # Check if minimum role constraints are met
        constraints_met = True
        for role, (min_count, max_count) in role_constraints.items():
            if role_counts.get(role, 0) < min_count:
                constraints_met = False
                print(f"⚠️  Warning: Minimum constraint for {role} not met ({role_counts.get(role, 0)} < {min_count})")
        
        # Create result DataFrame
        selected_df = pd.DataFrame(selected)
        
        result = {
            'status': 'Feasible' if constraints_met else 'Suboptimal',
            'method': 'Greedy',
            'selected_players': selected_df.to_dict('records') if not selected_df.empty else [],
            'total_players': len(selected_df),
            'total_performance': float(selected_df['predicted_performance'].sum()) if not selected_df.empty else 0,
            'total_salary': float(total_salary),
            'salary_remaining': float(salary_cap - total_salary),
            'avg_value_index': float(selected_df['value_index'].mean()) if not selected_df.empty else 0,
            'role_distribution': dict(role_counts),
            'constraints_met': constraints_met
        }
        
        # Display results
        print("\n" + "=" * 70)
        print("Optimization Results (Greedy)")
        print("=" * 70)
        print(f"Total Players Selected: {result['total_players']}")
        print(f"Total Performance: {result['total_performance']:.2f}")
        print(f"Total Salary: {result['total_salary']:,.0f} lakhs")
        print(f"Salary Remaining: {result['salary_remaining']:,.0f} lakhs")
        print(f"Average Value Index: {result['avg_value_index']:.4f}")
        print(f"\nRole Distribution:")
        for role, count in role_counts.items():
            print(f"  {role}: {count} players")
        
        return result
    
    def compare_rosters(
        self,
        current_roster: pd.DataFrame,
        optimized_roster: pd.DataFrame
    ) -> Dict:
        """
        Compare current roster with optimized roster.
        
        Args:
            current_roster: Current roster DataFrame
            optimized_roster: Optimized roster DataFrame
            
        Returns:
            Comparison metrics
        """
        comparison = {
            'current': {
                'total_players': len(current_roster),
                'total_performance': float(current_roster['predicted_performance'].sum()),
                'total_salary': float(current_roster['salary_lakhs'].sum()),
                'avg_value_index': float(current_roster['value_index'].mean())
            },
            'optimized': {
                'total_players': len(optimized_roster),
                'total_performance': float(optimized_roster['predicted_performance'].sum()),
                'total_salary': float(optimized_roster['salary_lakhs'].sum()),
                'avg_value_index': float(optimized_roster['value_index'].mean())
            },
            'improvement': {}
        }
        
        # Calculate improvements
        comparison['improvement'] = {
            'performance': float(
                comparison['optimized']['total_performance'] - 
                comparison['current']['total_performance']
            ),
            'performance_pct': float(
                (comparison['optimized']['total_performance'] / 
                 comparison['current']['total_performance'] - 1) * 100
            ) if comparison['current']['total_performance'] > 0 else 0,
            'salary': float(
                comparison['optimized']['total_salary'] - 
                comparison['current']['total_salary']
            ),
            'value_index': float(
                comparison['optimized']['avg_value_index'] - 
                comparison['current']['avg_value_index']
            )
        }
        
        return comparison


if __name__ == "__main__":
    # Test the optimizer
    print("Testing Roster Optimizer...")
    
    # Load sample data
    import sys
    sys.path.append('..')
    
    try:
        df = pd.read_csv('../../data/players_with_predictions.csv')
        print(f"✓ Loaded {len(df)} players with predictions")
        
        # Initialize optimizer
        optimizer = RosterOptimizer()
        
        # Run optimization
        result = optimizer.optimize_roster(
            players_df=df,
            salary_cap=10000,  # 100 crore (10000 lakhs)
            roster_size=25,
            role_constraints={
                'Batsman': (6, 10),
                'Bowler': (6, 10),
                'Allrounder': (3, 6),
                'Wicketkeeper': (1, 3)
            }
        )
        
        print("\n✓ Optimization test completed successfully!")
        
    except FileNotFoundError:
        print("⚠️  Prediction file not found. Run ml_model.py --predict first.")
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
