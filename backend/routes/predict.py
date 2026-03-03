"""
Predict Route for Apex Zero API

Handles ML model predictions on player data.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import os

from backend.schemas.player_schema import (
    PredictRequest, PredictResponse, PlayerWithPredictions, ErrorResponse
)
from backend.services.ml_model import RosterOptimizationModel
from backend.utils.helpers import check_model_exists, load_csv_safe

router = APIRouter(prefix="/predict", tags=["Predictions"])

# Global model instance (loaded on first use)
_model_instance = None


def get_model():
    """Get or create model instance."""
    global _model_instance
    if _model_instance is None:
        _model_instance = RosterOptimizationModel()
    return _model_instance


@router.post("/", response_model=PredictResponse)
async def generate_predictions(request: PredictRequest = PredictRequest()):
    """
    Generate ML predictions for all players.
    
    - Loads trained model
    - Generates predictions for all players
    - Calculates value_index
    - Saves predictions to CSV
    
    Args:
        request: Prediction request (optional dataset path)
        
    Returns:
        PredictResponse with status and file path
    """
    # Check if model exists
    if not check_model_exists():
        raise HTTPException(
            status_code=404,
            detail="Trained model not found. Please train the model first."
        )
    
    # Determine dataset path
    dataset_path = request.dataset_path if request.dataset_path else "data/players_clean.csv"
    
    if not os.path.exists(dataset_path):
        raise HTTPException(
            status_code=404,
            detail=f"Dataset not found at {dataset_path}"
        )
    
    try:
        # Get model instance
        model = get_model()
        
        # Generate predictions
        predictions_df = model.predict(filepath=dataset_path)
        
        return PredictResponse(
            status="success",
            message="Predictions generated successfully",
            players_count=len(predictions_df),
            model_type=model.model_type,
            predictions_path="data/players_with_predictions.csv"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating predictions: {str(e)}"
        )


@router.get("/players", response_model=List[PlayerWithPredictions])
async def get_all_predictions(
    limit: Optional[int] = None,
    offset: int = 0,
    sort_by: str = "value_index",
    ascending: bool = False
):
    """
    Get all players with predictions.
    
    - Returns list of players with ML predictions
    - Supports pagination
    - Supports sorting
    
    Args:
        limit: Maximum number of players to return
        offset: Number of players to skip
        sort_by: Column to sort by
        ascending: Sort order
        
    Returns:
        List of players with predictions
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        
        # Sort
        if sort_by in df.columns:
            df = df.sort_values(sort_by, ascending=ascending)
        
        # Paginate
        if limit:
            df = df.iloc[offset:offset+limit]
        else:
            df = df.iloc[offset:]
        
        # Convert to dict records
        players = df.to_dict('records')
        
        return players
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving predictions: {str(e)}"
        )


@router.get("/players/{player_name}", response_model=PlayerWithPredictions)
async def get_player_prediction(player_name: str):
    """
    Get predictions for a specific player.
    
    Args:
        player_name: Name of the player
        
    Returns:
        Player data with predictions
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        
        # Find player (case-insensitive)
        player_df = df[df['Player'].str.lower() == player_name.lower()]
        
        if player_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Player not found: {player_name}"
            )
        
        player = player_df.iloc[0].to_dict()
        
        return player
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving player: {str(e)}"
        )


@router.get("/top-value", response_model=List[PlayerWithPredictions])
async def get_top_value_players(limit: int = 10):
    """
    Get top value players (highest value_index).
    
    Args:
        limit: Number of players to return
        
    Returns:
        List of top value players
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        
        # Get top value players
        top_players = df.nlargest(limit, 'value_index')
        
        return top_players.to_dict('records')
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving top value players: {str(e)}"
        )


@router.get("/overpaid", response_model=List[PlayerWithPredictions])
async def get_overpaid_players(
    limit: int = 10,
    min_salary: float = 100
):
    """
    Get most overpaid players (lowest value_index).
    
    Args:
        limit: Number of players to return
        min_salary: Minimum salary threshold (lakhs)
        
    Returns:
        List of overpaid players
    """
    predictions_path = "data/players_with_predictions.csv"
    
    if not os.path.exists(predictions_path):
        raise HTTPException(
            status_code=404,
            detail="Predictions not found. Run POST /predict first."
        )
    
    try:
        df = load_csv_safe(predictions_path)
        
        # Filter by minimum salary
        filtered = df[df['salary_lakhs'] >= min_salary]
        
        # Get most overpaid
        overpaid = filtered.nsmallest(limit, 'value_index')
        
        return overpaid.to_dict('records')
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving overpaid players: {str(e)}"
        )


@router.get("/status")
async def get_prediction_status():
    """
    Check prediction status.
    
    Returns:
        Status information about predictions
    """
    model_exists = check_model_exists()
    predictions_path = "data/players_with_predictions.csv"
    predictions_exist = os.path.exists(predictions_path)
    
    status = {
        "model_trained": model_exists,
        "predictions_generated": predictions_exist
    }
    
    if predictions_exist:
        try:
            df = load_csv_safe(predictions_path)
            status["players_count"] = len(df)
            status["last_modified"] = os.path.getmtime(predictions_path)
            
            # Add model info if model is loaded
            if _model_instance and _model_instance.model:
                status["model_type"] = _model_instance.model_type
                status["model_metrics"] = _model_instance.metrics
        except Exception as e:
            status["error"] = str(e)
    
    return status
