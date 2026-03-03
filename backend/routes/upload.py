"""
Upload Route for Apex Zero API

Handles CSV file uploads and triggers preprocessing.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
import shutil
from typing import Optional

from backend.schemas.player_schema import UploadResponse, ErrorResponse
from backend.utils.helpers import ensure_directory_exists, validate_player_dataframe

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload player dataset CSV file.
    
    - Accepts CSV file
    - Validates required columns
    - Saves to data/players_clean.csv
    - Returns upload confirmation
    
    Args:
        file: CSV file upload
        
    Returns:
        UploadResponse with status and player count
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted"
        )
    
    try:
        # Read uploaded file
        contents = await file.read()
        
        # Create temporary file
        temp_path = f"data/temp_{file.filename}"
        ensure_directory_exists(temp_path)
        
        with open(temp_path, 'wb') as f:
            f.write(contents)
        
        # Load and validate CSV
        try:
            df = pd.read_csv(temp_path)
        except Exception as e:
            os.remove(temp_path)
            raise HTTPException(
                status_code=400,
                detail=f"Error reading CSV file: {str(e)}"
            )
        
        # Validate required columns
        try:
            validate_player_dataframe(df)
        except ValueError as e:
            os.remove(temp_path)
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        # Save to standard location
        final_path = "data/players_clean.csv"
        shutil.move(temp_path, final_path)
        
        return UploadResponse(
            status="success",
            message="Dataset uploaded successfully",
            players_count=len(df),
            filepath=final_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing upload: {str(e)}"
        )
    finally:
        # Cleanup
        await file.close()


@router.post("/validate", response_model=dict)
async def validate_dataset(file: UploadFile = File(...)):
    """
    Validate dataset without saving.
    
    - Checks file format
    - Validates required columns
    - Returns validation results
    
    Args:
        file: CSV file to validate
        
    Returns:
        Validation results
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted"
        )
    
    try:
        contents = await file.read()
        
        # Save temporarily for validation
        temp_path = f"data/temp_validate_{file.filename}"
        ensure_directory_exists(temp_path)
        
        with open(temp_path, 'wb') as f:
            f.write(contents)
        
        # Load CSV
        df = pd.read_csv(temp_path)
        
        # Validate
        validation_results = {
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }
        
        # Check required columns
        required_columns = [
            'Player', 'TEAM', 'AGE', 'Paying_Role', 'Mat', 'Runs', 
            'Avg', 'SR', 'B_Inns', 'B_Wkts', 'B_Econ', 'salary_lakhs'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        validation_results["required_columns_present"] = len(missing_columns) == 0
        validation_results["missing_columns"] = missing_columns
        
        # Check data types
        validation_results["data_types"] = {
            col: str(df[col].dtype) for col in df.columns
        }
        
        # Check for null values
        validation_results["null_counts"] = df.isnull().sum().to_dict()
        
        # Clean up
        os.remove(temp_path)
        
        return validation_results
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=500,
            detail=f"Error validating file: {str(e)}"
        )
    finally:
        await file.close()


@router.get("/status")
async def get_upload_status():
    """
    Check if dataset is uploaded and ready.
    
    Returns:
        Status information about uploaded dataset
    """
    dataset_path = "data/players_clean.csv"
    
    if not os.path.exists(dataset_path):
        return {
            "dataset_uploaded": False,
            "message": "No dataset uploaded yet"
        }
    
    try:
        df = pd.read_csv(dataset_path)
        
        return {
            "dataset_uploaded": True,
            "filepath": dataset_path,
            "players_count": len(df),
            "last_modified": os.path.getmtime(dataset_path),
            "columns": list(df.columns)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading dataset: {str(e)}"
        )
