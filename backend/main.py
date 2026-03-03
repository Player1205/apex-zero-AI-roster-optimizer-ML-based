"""
Apex Zero Roster Optimizer - Main FastAPI Application

An AI-driven Roster & Contract Optimizer SaaS app for IPL teams.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from backend.routes import upload, predict, optimize, dashboard
from backend.schemas.player_schema import HealthResponse, ErrorResponse
from backend.utils.helpers import check_model_exists, check_predictions_exist

# Create FastAPI app   
app = FastAPI(
    title="Apex Zero Roster Optimizer API",
    description="AI-driven Roster & Contract Optimizer for IPL teams",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(optimize.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Apex Zero Roster Optimizer API",
        "version": "1.0.0",
        "description": "AI-driven Roster & Contract Optimizer for IPL teams",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "upload": "/api/upload",
            "predict": "/api/predict",
            "optimize": "/api/optimize",
            "dashboard": "/api/dashboard"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service health status
    """
    model_exists = check_model_exists('backend/models/model.pkl')
    predictions_exist = check_predictions_exist('data/players_with_predictions.csv')
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded=model_exists and predictions_exist
    )


@app.get("/status", tags=["Status"])
async def get_status():
    """
    Get detailed API status.
    
    Returns:
        Detailed status information
    """
    dataset_path = "data/players_clean.csv"
    model_path = "backend/models/model.pkl"
    predictions_path = "data/players_with_predictions.csv"
    
    status = {
        "api": "running",
        "version": "1.0.0",
        "dataset": {
            "uploaded": os.path.exists(dataset_path),
            "path": dataset_path if os.path.exists(dataset_path) else None
        },
        "model": {
            "trained": os.path.exists(model_path),
            "path": model_path if os.path.exists(model_path) else None
        },
        "predictions": {
            "generated": os.path.exists(predictions_path),
            "path": predictions_path if os.path.exists(predictions_path) else None
        }
    }
    
    # Add player count if dataset exists
    if status["dataset"]["uploaded"]:
        try:
            import pandas as pd
            df = pd.read_csv(dataset_path)
            status["dataset"]["players_count"] = len(df)
        except:
            pass
    
    # Add predictions count if predictions exist
    if status["predictions"]["generated"]:
        try:
            import pandas as pd
            df = pd.read_csv(predictions_path)
            status["predictions"]["players_count"] = len(df)
        except:
            pass
    
    return status


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            status="error",
            message="Resource not found",
            detail=str(exc.detail) if hasattr(exc, 'detail') else None
        ).dict()
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status="error",
            message="Internal server error",
            detail=str(exc)
        ).dict()
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on startup."""
    print("=" * 70)
    print("Apex Zero Roster Optimizer API")
    print("=" * 70)
    print("Starting server...")
    
    # Ensure directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("backend/models", exist_ok=True)
    
    # Check status
    model_exists = check_model_exists('backend/models/model.pkl')
    dataset_exists = os.path.exists("data/players_clean.csv")
    predictions_exist = check_predictions_exist('data/players_with_predictions.csv')
    
    print(f"\nStatus:")
    print(f"  Dataset: {'✓' if dataset_exists else '✗'}")
    print(f"  Model: {'✓' if model_exists else '✗'}")
    print(f"  Predictions: {'✓' if predictions_exist else '✗'}")
    
    if not model_exists:
        print("\n⚠️  Warning: Model not found. Train model using:")
        print("    cd backend/services && python ml_model.py --train")
    
    print("\n✓ Server ready!")
    print("  API Docs: http://localhost:8000/docs")
    print("  Health Check: http://localhost:8000/health")
    print("=" * 70)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown."""
    print("\nShutting down Apex Zero API...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
