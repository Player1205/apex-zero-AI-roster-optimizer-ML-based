"""
Dashboard Route for Apex Zero API

Provides analytics data for the dashboard.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import os

from backend.schemas.player_schema import DashboardResponse, ErrorResponse
from backend.services.trade_logic import TradeAnalyzer, ValueIndexAnalyzer
from backend.utils.helpers import load_csv_safe, create_summary_stats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
async def get_dashboard_data(limit: int = 10):
    """
    Get comprehensive dashboard data.
    
    Returns:
    - Overall statistics
    - Top undervalued players
    - Top overpaid players
    - Contract extension candidates
    - Value distribution
    - Role distribution
    - Salary distribution
    
    Args:
        limit: Number of players to return in each list
        
    Returns:
        Complete dashboard data
    """
    predictions_path = "./data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        # Load data
        df = load_csv_safe(predictions_path)
        
        # Initialize analyzer
        analyzer = TradeAnalyzer()
        analyzer.players_df = df
        
        # Get overall statistics
        stats = create_summary_stats(df)
        
        # Get top undervalued players
        undervalued = analyzer.identify_undervalued(top_n=limit)
        
        # Get top overpaid players
        overpaid = analyzer.identify_overpaid(top_n=limit)
        
        # Get contract extension candidates
        extensions = analyzer.suggest_contract_extensions(top_n=limit)
        
        # Get value distribution
        value_dist = ValueIndexAnalyzer.get_value_distribution(df)
        
        # Format value distribution for response
        value_categories = [
            {
                "category": category,
                "count": value_dist['category_counts'][category],
                "percentage": value_dist['category_percentages'][category]
            }
            for category in ['elite_value', 'good_value', 'fair_value', 'poor_value', 'overpaid']
        ]
        
        # Get role distribution
        role_distribution = df['Paying_Role'].value_counts().to_dict()
        
        # Calculate salary distribution
        salary_dist = {
            'total': float(df['salary_lakhs'].sum()),
            'mean': float(df['salary_lakhs'].mean()),
            'median': float(df['salary_lakhs'].median()),
            'std': float(df['salary_lakhs'].std()),
            'min': float(df['salary_lakhs'].min()),
            'max': float(df['salary_lakhs'].max()),
            'quartiles': {
                'q1': float(df['salary_lakhs'].quantile(0.25)),
                'q2': float(df['salary_lakhs'].quantile(0.50)),
                'q3': float(df['salary_lakhs'].quantile(0.75))
            }
        }
        
        return DashboardResponse(
            stats={
                "total_players": stats['total_players'],
                "total_salary": stats['total_salary'],
                "avg_salary": stats['avg_salary'],
                "avg_performance": stats.get('avg_performance', 0),
                "avg_value_index": stats.get('avg_value_index', 0)
            },
            top_undervalued=undervalued.to_dict('records'),
            top_overpaid=overpaid.to_dict('records'),
            contract_extensions=extensions.to_dict('records'),
            value_distribution=value_categories,
            role_distribution=role_distribution,
            salary_distribution=salary_dist
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating dashboard data: {str(e)}"
        )


@router.get("/summary")
async def get_summary_stats():
    """
    Get summary statistics only.
    
    Returns:
        Quick overview statistics
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        stats = create_summary_stats(df)
        
        return {
            "status": "success",
            "summary": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting summary: {str(e)}"
        )


@router.get("/value-distribution")
async def get_value_distribution():
    """
    Get detailed value index distribution.
    
    Returns:
        Value index distribution by category
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        
        # Get distribution
        value_dist = ValueIndexAnalyzer.get_value_distribution(df)
        
        # Get players by category
        categories = ValueIndexAnalyzer.categorize_players(df)
        
        result = {
            "status": "success",
            "distribution": value_dist,
            "players_by_category": {
                category: players_df[['Player', 'Paying_Role', 'salary_lakhs', 'value_index']].to_dict('records')
                for category, players_df in categories.items()
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting value distribution: {str(e)}"
        )


@router.get("/role-distribution")
async def get_role_distribution():
    """
    Get role distribution statistics.
    
    Returns:
        Distribution of players by role
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        
        role_dist = df['Paying_Role'].value_counts().to_dict()
        role_pct = (df['Paying_Role'].value_counts(normalize=True) * 100).to_dict()
        
        # Get average metrics by role
        role_stats = df.groupby('Paying_Role').agg({
            'salary_lakhs': 'mean',
            'predicted_performance': 'mean',
            'value_index': 'mean'
        }).to_dict('index')
        
        return {
            "status": "success",
            "role_counts": role_dist,
            "role_percentages": role_pct,
            "role_statistics": role_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting role distribution: {str(e)}"
        )


@router.get("/salary-distribution")
async def get_salary_distribution():
    """
    Get salary distribution statistics.
    
    Returns:
        Salary distribution with percentiles
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        
        # Calculate percentiles
        percentiles = [0, 10, 25, 50, 75, 90, 100]
        salary_percentiles = {
            f"p{p}": float(df['salary_lakhs'].quantile(p/100))
            for p in percentiles
        }
        
        # Get salary brackets
        brackets = {
            'under_100': len(df[df['salary_lakhs'] < 100]),
            '100_500': len(df[(df['salary_lakhs'] >= 100) & (df['salary_lakhs'] < 500)]),
            '500_1000': len(df[(df['salary_lakhs'] >= 500) & (df['salary_lakhs'] < 1000)]),
            'over_1000': len(df[df['salary_lakhs'] >= 1000])
        }
        
        return {
            "status": "success",
            "total_salary": float(df['salary_lakhs'].sum()),
            "mean": float(df['salary_lakhs'].mean()),
            "median": float(df['salary_lakhs'].median()),
            "std": float(df['salary_lakhs'].std()),
            "percentiles": salary_percentiles,
            "brackets": brackets
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting salary distribution: {str(e)}"
        )


@router.get("/team-comparison")
async def compare_teams():
    """
    Compare statistics across teams.
    
    Returns:
        Team-wise comparison of key metrics
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        
        # Group by team
        team_stats = df.groupby('TEAM').agg({
            'Player': 'count',
            'salary_lakhs': ['sum', 'mean'],
            'predicted_performance': ['sum', 'mean'],
            'value_index': 'mean'
        }).round(2)
        
        # Flatten column names
        team_stats.columns = ['_'.join(col).strip() for col in team_stats.columns.values]
        
        # Convert to dict
        team_comparison = team_stats.to_dict('index')
        
        return {
            "status": "success",
            "team_statistics": team_comparison
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing teams: {str(e)}"
        )


@router.get("/insights")
async def get_insights():
    """
    Get actionable insights and recommendations.
    
    Returns:
        Key insights derived from the data
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        
        insights = []
        
        # Insight 1: Overpaid players count
        overpaid_count = len(df[df['value_index'] < 0.05])
        if overpaid_count > 0:
            insights.append({
                "type": "warning",
                "category": "overpaid",
                "message": f"{overpaid_count} players are significantly overpaid (value_index < 0.05)",
                "action": "Consider trading these players"
            })
        
        # Insight 2: Undervalued players
        undervalued_count = len(df[df['value_index'] > 0.5])
        if undervalued_count > 0:
            insights.append({
                "type": "opportunity",
                "category": "undervalued",
                "message": f"{undervalued_count} players provide exceptional value (value_index > 0.5)",
                "action": "Prioritize contract extensions for these players"
            })
        
        # Insight 3: Salary concentration
        top_5_salary_pct = (df.nlargest(5, 'salary_lakhs')['salary_lakhs'].sum() / 
                           df['salary_lakhs'].sum() * 100)
        if top_5_salary_pct > 50:
            insights.append({
                "type": "warning",
                "category": "salary_concentration",
                "message": f"Top 5 earners account for {top_5_salary_pct:.1f}% of total salary",
                "action": "Consider diversifying salary distribution"
            })
        
        # Insight 4: Role balance
        role_counts = df['Paying_Role'].value_counts().to_dict()
        if role_counts.get('Bowler', 0) < 5:
            insights.append({
                "type": "warning",
                "category": "role_balance",
                "message": f"Only {role_counts.get('Bowler', 0)} bowlers in roster",
                "action": "Acquire more bowling talent"
            })
        
        return {
            "status": "success",
            "insights_count": len(insights),
            "insights": insights
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating insights: {str(e)}"
        )
