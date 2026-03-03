"""
Optimize Route for Apex Zero API

Handles roster optimization requests.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
import os

from backend.schemas.player_schema import (
    OptimizeRequest, OptimizeResponse, TradeSimulation, 
    TradeSimulationResponse, ErrorResponse
)
from backend.services.optimizer import RosterOptimizer
from backend.services.trade_logic import TradeAnalyzer
from backend.utils.helpers import load_csv_safe

router = APIRouter(prefix="/optimize", tags=["Optimization"])


@router.post("/roster", response_model=OptimizeResponse)
async def optimize_roster(request: OptimizeRequest):
    """
    Optimize team roster under constraints.
    
    - Maximizes predicted performance
    - Respects salary cap constraint
    - Respects roster size constraint
    - Respects role constraints
    - Uses MILP or greedy algorithm
    
    Args:
        request: Optimization request with constraints
        
    Returns:
        OptimizeResponse with selected players and metrics
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        # Load predictions
        df = load_csv_safe(predictions_path)
        
        # Convert role constraints to dict format
        role_constraints = None
        if request.role_constraints:
            role_constraints = {
                rc.role: (rc.min_count, rc.max_count) 
                for rc in request.role_constraints
            }
        
        # Initialize optimizer
        optimizer = RosterOptimizer()
        
        # Run optimization
        if request.use_greedy:
            result = optimizer.greedy_optimize(
                players_df=df,
                salary_cap=request.salary_cap,
                roster_size=request.roster_size,
                role_constraints=role_constraints
            )
        else:
            result = optimizer.optimize_roster(
                players_df=df,
                salary_cap=request.salary_cap,
                roster_size=request.roster_size,
                role_constraints=role_constraints
            )
        
        return OptimizeResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing roster: {str(e)}"
        )


@router.post("/trade-simulation", response_model=TradeSimulationResponse)
async def simulate_trade(trade: TradeSimulation):
    """
    Simulate a trade between two players.
    
    - Calculates trade impact on performance and salary
    - Provides trade recommendation
    
    Args:
        trade: Trade simulation request
        
    Returns:
        Trade impact analysis
    """
    try:
        # Initialize analyzer
        analyzer = TradeAnalyzer()
        analyzer.load_predictions()
        
        # Get full player data
        df = analyzer.players_df
        
        # Find players
        out_player = df[df['Player'] == trade.trade_out_player]
        in_player = df[df['Player'] == trade.trade_in_player]
        
        if out_player.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Player not found: {trade.trade_out_player}"
            )
        if in_player.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Player not found: {trade.trade_in_player}"
            )
        
        out_player = out_player.iloc[0].to_dict()
        in_player = in_player.iloc[0].to_dict()
        
        # Calculate trade impact
        impact = {
            'salary_change': float(in_player['salary_lakhs'] - out_player['salary_lakhs']),
            'performance_change': float(in_player['predicted_performance'] - out_player['predicted_performance']),
            'value_index_change': float(in_player['value_index'] - out_player['value_index'])
        }
        
        # Determine recommendation
        if impact['performance_change'] > 0 and impact['salary_change'] <= 0:
            recommendation = "Highly Recommended ✓✓✓"
        elif impact['performance_change'] > 0:
            recommendation = "Recommended ✓✓"
        elif impact['value_index_change'] > 0:
            recommendation = "Consider ✓"
        else:
            recommendation = "Not Recommended ✗"
        
        # Format response
        response = TradeSimulationResponse(
            trade_out=out_player,
            trade_in=in_player,
            impact=impact,
            recommendation=recommendation
        )
        
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error simulating trade: {str(e)}"
        )


@router.get("/trade-candidates")
async def get_trade_candidates(limit: int = 10):
    """
    Get trade candidate recommendations.
    
    Returns overpaid players who should be considered for trades.
    
    Args:
        limit: Number of candidates to return
        
    Returns:
        List of trade candidates
    """
    try:
        analyzer = TradeAnalyzer()
        analyzer.load_predictions()
        
        overpaid = analyzer.identify_overpaid(top_n=limit)
        
        return {
            "status": "success",
            "trade_candidates": overpaid.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting trade candidates: {str(e)}"
        )


@router.get("/acquisition-targets")
async def get_acquisition_targets(limit: int = 10, max_salary: float = 1000):
    """
    Get acquisition target recommendations.
    
    Returns undervalued players who should be considered for acquisition.
    
    Args:
        limit: Number of targets to return
        max_salary: Maximum salary threshold (lakhs)
        
    Returns:
        List of acquisition targets
    """
    try:
        analyzer = TradeAnalyzer()
        analyzer.load_predictions()
        
        undervalued = analyzer.identify_undervalued(
            top_n=limit,
            max_salary=max_salary
        )
        
        return {
            "status": "success",
            "acquisition_targets": undervalued.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting acquisition targets: {str(e)}"
        )


@router.get("/contract-extensions")
async def get_contract_extensions(
    limit: int = 10,
    min_value_index: float = 0.3,
    max_salary: float = 800
):
    """
    Get contract extension recommendations.
    
    Returns players who should be considered for contract extensions.
    
    Args:
        limit: Number of players to return
        min_value_index: Minimum value index threshold
        max_salary: Maximum salary threshold (lakhs)
        
    Returns:
        List of extension candidates
    """
    try:
        analyzer = TradeAnalyzer()
        analyzer.load_predictions()
        
        extensions = analyzer.suggest_contract_extensions(
            top_n=limit,
            min_value_index=min_value_index,
            max_salary=max_salary
        )
        
        return {
            "status": "success",
            "extension_candidates": extensions.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting contract extensions: {str(e)}"
        )


@router.get("/compare-rosters")
async def compare_rosters(
    current_roster_ids: str,  # Comma-separated player names
    optimized_roster_ids: str
):
    """
    Compare two rosters.
    
    Args:
        current_roster_ids: Comma-separated player names for current roster
        optimized_roster_ids: Comma-separated player names for optimized roster
        
    Returns:
        Comparison metrics
    """
    try:
        df = load_csv_safe("data/players_with_predictions.csv")
        
        # Parse player names
        current_players = [p.strip() for p in current_roster_ids.split(',')]
        optimized_players = [p.strip() for p in optimized_roster_ids.split(',')]
        
        # Get rosters
        current_roster = df[df['Player'].isin(current_players)]
        optimized_roster = df[df['Player'].isin(optimized_players)]
        
        if current_roster.empty or optimized_roster.empty:
            raise HTTPException(
                status_code=404,
                detail="One or more players not found"
            )
        
        # Compare
        optimizer = RosterOptimizer()
        comparison = optimizer.compare_rosters(current_roster, optimized_roster)
        
        return {
            "status": "success",
            "comparison": comparison
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing rosters: {str(e)}"
        )


@router.get("/team-analysis")
async def analyze_team(team_name: Optional[str] = None):
    """
    Analyze team composition and identify issues.
    
    Args:
        team_name: Team name to analyze (optional, analyzes all if not provided)
        
    Returns:
        Team analysis with issues and recommendations
    """
    try:
        analyzer = TradeAnalyzer()
        analyzer.load_predictions()
        
        analysis = analyzer.analyze_team_composition(team_name=team_name)
        
        return {
            "status": "success",
            "team": team_name if team_name else "All Teams",
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing team: {str(e)}"
        )
