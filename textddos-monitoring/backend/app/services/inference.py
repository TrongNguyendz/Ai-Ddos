# app/services/inference.py
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger

# ====================== CẤU HÌNH ======================
# Dùng đường dẫn động tương đối với file này (hoạt động cả Windows lẫn Linux)
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # → /app
MODEL_PATH = BASE_DIR / "models"
RF_MODEL_PATH = MODEL_PATH / "random_forest_model.pkl"
SCALER_PATH = MODEL_PATH / "scaler_fs.pkl"   # hoặc scaler.pkl

# Load model & scaler một lần khi import
rf_model = None
scaler = None

def load_models():
    global rf_model, scaler
    try:
        rf_model = joblib.load(RF_MODEL_PATH)
        logger.success(f"✅ Loaded Random Forest model: {RF_MODEL_PATH}")
        
        if SCALER_PATH.exists():
            scaler = joblib.load(SCALER_PATH)
            logger.success("✅ Loaded scaler")
        else:
            logger.warning("⚠️ Không tìm thấy scaler, sẽ dùng raw features")
    except Exception as e:
        logger.error(f"❌ Load model thất bại: {e}")

# Load ngay khi import
load_models()

def predict_flow(flow_dict: dict) -> dict:
    """
    Dự đoán bằng Random Forest
    Input: dict từ packet sniffer
    Output: {"label": 0/1, "confidence": float}
    """
    global rf_model, scaler
    
    if rf_model is None:
        logger.error("Model chưa được load!")
        return {"label": 0, "confidence": 0.5}

    try:
        # Chuẩn bị features theo đúng thứ tự model được train
        features = [
            flow_dict.get("pktcount", 0),
            flow_dict.get("byteperflow", 0.0),
            flow_dict.get("tot_kbps", 0.0),
            flow_dict.get("rx_kbps", 0.0),
            flow_dict.get("flows", 1),
            flow_dict.get("bytecount", 0),
            flow_dict.get("tot_dur", 0.0),
            flow_dict.get("protocol_icmp", 0),
            flow_dict.get("protocol_tcp", 0),
            flow_dict.get("protocol_udp", 0),
        ]

        df = pd.DataFrame([features], columns=[
            'pktcount', 'byteperflow', 'tot_kbps', 'rx_kbps',
            'flows', 'bytecount', 'tot_dur',
            'Protocol_ICMP', 'Protocol_TCP', 'Protocol_UDP'
        ])

        # Scale nếu có
        if scaler is not None:
            scaled = scaler.transform(df)
        else:
            scaled = df.values

        # Dự đoán
        pred = rf_model.predict(scaled)[0]
        proba = rf_model.predict_proba(scaled)[0]
        
        confidence = float(max(proba))
        label = int(pred)

        return {
            "label": label,           # 0 = Benign, 1 = Malicious
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"label": 0, "confidence": 0.6}