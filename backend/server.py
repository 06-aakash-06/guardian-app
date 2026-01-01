# backend/server.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import cv2
import io
import numpy as np
from PIL import Image

# Import your existing modules
from analyzer_content import AnalyzerContent
from analyzer_forensics import AnalyzerForensics
from analyzer_metadata import AnalyzerMetadata
from risk_engine import RiskEngine
from protection_tools import ProtectionTools

app = FastAPI()

# Allow React to talk to Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Tools
content_analyzer = AnalyzerContent()
forensics_analyzer = AnalyzerForensics()
metadata_analyzer = AnalyzerMetadata()
risk_engine = RiskEngine()
protection_tools = ProtectionTools()

CURRENT_IMG_PATH = "temp_session.jpg"

@app.post("/api/scan")
async def scan_image(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        with open(CURRENT_IMG_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load image
        img_bgr = cv2.imread(CURRENT_IMG_PATH)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # Run Analysis
        faces, is_child = content_analyzer.analyze_faces(img_rgb)
        barcodes = content_analyzer.scan_barcodes(img_rgb)
        pii = content_analyzer.scan_text_pii(img_rgb)
        ela_status = forensics_analyzer.analyze_ela(img_rgb)
        meta_report = metadata_analyzer.get_metadata_risk(CURRENT_IMG_PATH)

        # Score
        all_detections = faces + barcodes
        score, threats = risk_engine.calculate_trust_score(
            {'ela_manipulated': ela_status}, all_detections, is_child, pii, barcodes, meta_report
        )

        return {
            "score": score,
            "status": "SAFE" if score > 50 else "HIGH RISK",
            "threats": threats,
            "detections": all_detections,
            "meta": meta_report
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/protect")
async def protect_image(action: str = Form(...), indices: str = Form("")):
    try:
        img_bgr = cv2.imread(CURRENT_IMG_PATH)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        # Re-detect for coordinates
        faces, _ = content_analyzer.analyze_faces(img_rgb)
        barcodes = content_analyzer.scan_barcodes(img_rgb)
        all_detections = faces + barcodes

        if action == "blur_selected":
            target_indices = [int(x) for x in indices.split(",") if x]
            items = [all_detections[i] for i in target_indices if i < len(all_detections)]
            img_rgb = protection_tools.smart_redact(img_rgb, items)
        elif action == "cloak":
            for face in faces:
                img_rgb = protection_tools.cloak_face(img_rgb, face['box'])

        # Return Image
        final_pil = Image.fromarray(img_rgb)
        img_byte_arr = io.BytesIO()
        final_pil.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))