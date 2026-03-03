"""
Pydantic Schemas for Apex Zero API

Defines data validation and serialization schemas for all API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from enum import Enum


class PayingRole(str, Enum):
    """Player role enumeration."""
    BATSMAN = "Batsman"
    BOWLER = "Bowler"
    ALLROUNDER = "Allrounder"
    WICKETKEEPER = "Wicketkeeper"


class PlayerBase(BaseModel):
    """Base player schema."""
    Player: str = Field(..., description="Player name")
    TEAM: str = Field(..., description="IPL team")
    AGE: int = Field(..., ge=15, le=50, description="Player age")
    Paying_Role: str = Field(..., description="Player role")
    Mat: int = Field(..., ge=0, description="Matches played")
    Runs: int = Field(..., ge=0, description="Total runs")
    Avg: float = Field(..., ge=0, description="Batting average")
    SR: float = Field(..., ge=0, description="Strike rate")
    B_Inns: int = Field(..., ge=0, description="Bowling innings")
    B_Wkts: int = Field(..., ge=0, description="Wickets taken")
    B_Econ: float = Field(..., ge=0, description="Economy rate")
    salary_lakhs: float = Field(..., ge=0, description="Salary in lakhs INR")


class PlayerWithPredictions(PlayerBase):
    """Player schema with ML predictions."""
    runs_per_match: Optional[float] = Field(None, description="Engineered: Runs per match")
    wickets_per_match: Optional[float] = Field(None, description="Engineered: Wickets per match")
    batting_impact: Optional[float] = Field(None, description="Engineered: Batting impact score")
    bowling_impact: Optional[float] = Field(None, description="Engineered: Bowling impact score")
    performance_score: Optional[float] = Field(None, description="Overall performance score")
    predicted_performance: Optional[float] = Field(None, description="ML predicted performance")
    value_index: Optional[float] = Field(None, description="Performance per salary unit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "Player": "Virat Kohli",
                "TEAM": "RCB",
                "AGE": 35,
                "Paying_Role": "Batsman",
                "Mat": 223,
                "Runs": 7263,
                "Avg": 37.25,
                "SR": 130.4,
                "B_Inns": 0,
                "B_Wkts": 0,
                "B_Econ": 0.0,
                "salary_lakhs": 1700,
                "predicted_performance": 32.54,
                "value_index": 0.019
            }
        }


class UploadResponse(BaseModel):
    """Response for file upload."""
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")
    players_count: int = Field(..., description="Number of players loaded")
    filepath: str = Field(..., description="File save location")


class PredictRequest(BaseModel):
    """Request for generating predictions."""
    dataset_path: Optional[str] = Field(None, description="Path to dataset (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dataset_path": "data/players_clean.csv"
            }
        }


class PredictResponse(BaseModel):
    """Response with predictions."""
    status: str = Field(..., description="Prediction status")
    message: str = Field(..., description="Status message")
    players_count: int = Field(..., description="Number of players predicted")
    model_type: str = Field(..., description="ML model used")
    predictions_path: str = Field(..., description="Path to predictions file")


class RoleConstraint(BaseModel):
    """Role constraint for optimization."""
    role: str = Field(..., description="Player role")
    min_count: int = Field(..., ge=0, description="Minimum players required")
    max_count: int = Field(..., ge=0, description="Maximum players allowed")
    
    @validator('max_count')
    def max_greater_than_min(cls, v, values):
        if 'min_count' in values and v < values['min_count']:
            raise ValueError('max_count must be >= min_count')
        return v


class OptimizeRequest(BaseModel):
    """Request for roster optimization."""
    salary_cap: float = Field(..., gt=0, description="Maximum salary cap in lakhs")
    roster_size: int = Field(25, ge=11, le=30, description="Number of players to select")
    role_constraints: Optional[List[RoleConstraint]] = Field(
        None, 
        description="Role-based constraints"
    )
    use_greedy: bool = Field(False, description="Force greedy algorithm instead of MILP")
    
    class Config:
        json_schema_extra = {
            "example": {
                "salary_cap": 10000,
                "roster_size": 25,
                "role_constraints": [
                    {"role": "Batsman", "min_count": 6, "max_count": 10},
                    {"role": "Bowler", "min_count": 6, "max_count": 10},
                    {"role": "Allrounder", "min_count": 3, "max_count": 6},
                    {"role": "Wicketkeeper", "min_count": 1, "max_count": 3}
                ],
                "use_greedy": False
            }
        }


class OptimizeResponse(BaseModel):
    """Response with optimized roster."""
    status: str = Field(..., description="Optimization status")
    method: str = Field(..., description="Optimization method used (MILP or Greedy)")
    selected_players: List[PlayerWithPredictions] = Field(..., description="Selected players")
    total_players: int = Field(..., description="Total players selected")
    total_performance: float = Field(..., description="Total predicted performance")
    total_salary: float = Field(..., description="Total salary in lakhs")
    salary_remaining: float = Field(..., description="Remaining salary cap")
    avg_value_index: float = Field(..., description="Average value index")
    role_distribution: Dict[str, int] = Field(..., description="Distribution by role")
    constraints_met: bool = Field(..., description="Whether all constraints were met")


class TradeSimulation(BaseModel):
    """Trade simulation request."""
    trade_out_player: str = Field(..., description="Player to trade away")
    trade_in_player: str = Field(..., description="Player to acquire")
    
    class Config:
        json_schema_extra = {
            "example": {
                "trade_out_player": "Jasprit Bumrah",
                "trade_in_player": "Rashid Khan"
            }
        }


class TradeImpact(BaseModel):
    """Trade impact analysis."""
    salary_change: float = Field(..., description="Change in salary")
    performance_change: float = Field(..., description="Change in performance")
    value_index_change: float = Field(..., description="Change in value index")


class TradeSimulationResponse(BaseModel):
    """Response for trade simulation."""
    trade_out: PlayerWithPredictions = Field(..., description="Player being traded away")
    trade_in: PlayerWithPredictions = Field(..., description="Player being acquired")
    impact: TradeImpact = Field(..., description="Trade impact metrics")
    recommendation: str = Field(..., description="Trade recommendation")


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_players: int = Field(..., description="Total players in dataset")
    total_salary: float = Field(..., description="Total salary across all players")
    avg_salary: float = Field(..., description="Average salary")
    avg_performance: float = Field(..., description="Average predicted performance")
    avg_value_index: float = Field(..., description="Average value index")


class ValueCategory(BaseModel):
    """Value index category."""
    category: str = Field(..., description="Category name")
    count: int = Field(..., description="Number of players")
    percentage: float = Field(..., description="Percentage of total")

class Quartiles(BaseModel):
    q1: float
    q2: float
    q3: float


class SalaryDistribution(BaseModel):
    min: float
    max: float
    mean: float
    quartiles: Quartiles

class DashboardResponse(BaseModel):
    """Response for dashboard endpoint."""
    stats: DashboardStats = Field(..., description="Overall statistics")
    top_undervalued: List[PlayerWithPredictions] = Field(..., description="Top undervalued players")
    top_overpaid: List[PlayerWithPredictions] = Field(..., description="Top overpaid players")
    contract_extensions: List[PlayerWithPredictions] = Field(..., description="Contract extension candidates")
    value_distribution: List[ValueCategory] = Field(..., description="Value index distribution")
    role_distribution: Dict[str, int] = Field(..., description="Role distribution")
    salary_distribution: Dict[str, object] = Field(..., description="Salary distribution stats")


class ErrorResponse(BaseModel):
    """Error response schema."""
    status: str = Field("error", description="Status")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "File not found",
                "detail": "Could not locate data/players_clean.csv"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field("healthy", description="Service status")
    version: str = Field("1.0.0", description="API version")
    models_loaded: bool = Field(..., description="Whether ML models are loaded")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "models_loaded": True
            }
        }
