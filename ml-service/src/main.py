import torch
import torch.nn as nn
import joblib
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from preprocess import URLExtractor
from train import PhishingSentinelModel # Import the architecture
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sentinel Intelligence API")

# Enable CORS for the Go API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and scaler
MODEL = None
SCALER = None
EXTRACTOR = URLExtractor()

def load_assets():
    global MODEL, SCALER
    try:
        model_path = "models/sentinel_v1.pth"
        scaler_path = "models/scaler.pkl"
        
        # Load Scaler
        SCALER = joblib.load(scaler_path)
        
        # Load Model
        MODEL = PhishingSentinelModel(input_size=41) # Matches your 41 features
        MODEL.load_state_dict(torch.load(model_path))
        MODEL.eval()
        print("[Sentinel] Model and Scaler loaded successfully.")
    except Exception as e:
        print(f"Error loading assets: {e}")

class AnalysisRequest(BaseModel):
    url: str
    dom_content: str = "" # Optional for now, since model is lexical-based

@app.on_event("startup")
async def startup_event():
    load_assets()

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    if MODEL is None or SCALER is None:
        raise HTTPException(status_code=500, detail="Model assets not loaded")

    # 1. Extract Features from the URL
    features = EXTRACTOR.extract_features(request.url)
    
    # 2. Scale Features
    features_scaled = SCALER.transform(features)
    features_tensor = torch.FloatTensor(features_scaled)

    # 3. Predict
    with torch.no_grad():
        output = MODEL(features_tensor)
        confidence = output.item()
        is_spoof = confidence > 0.5

    # 4. Generate metadata for the dashboard
    threat_level = "high" if confidence > 0.8 else "medium" if is_spoof else "low"
    
    return {
        "is_spoof": is_spoof,
        "confidence_score": confidence,
        "threat_level": threat_level,
        "detected_anomalies": ["URL Lexical Pattern Match"] if is_spoof else []
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)