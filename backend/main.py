# main.py
import argparse
import os
from config import Config
from utils_io import load_image_safe, save_image_safe
from analyzer_forensics import AnalyzerForensics
from analyzer_content import AnalyzerContent
from analyzer_metadata import AnalyzerMetadata
from risk_engine import RiskEngine
from protection_tools import ProtectionTools

def main():
    parser = argparse.ArgumentParser(description="Guardian AI - Universal Safety Suite")
    parser.add_argument("--image", required=True, help="Path to image file")
    args = parser.parse_args()

    print(f"[*] Loading {args.image}...")
    
    try:
        image = load_image_safe(args.image)
        # Initialize Tools
        forensics = AnalyzerForensics()
        content = AnalyzerContent()
        metadata_tool = AnalyzerMetadata()
        risk_engine = RiskEngine()
        protector = ProtectionTools()
    except Exception as e:
        print(f"[!] Error loading system: {e}")
        return

    # --- ANALYSIS PHASE ---
    print("[*] Running Analysis Modules...")
    faces, is_child = content.analyze_faces(image)
    barcodes = content.scan_barcodes(image)
    pii = content.scan_text_pii(image)
    meta_report = metadata_tool.get_metadata_risk(args.image)
    ela_status = forensics.analyze_ela(image)

    # Combine detections for tracking
    # We add an 'index' so the user can select them later
    all_detections = faces + barcodes

    # Calculate Score
    forensics_report = {'ela_manipulated': ela_status}
    score, threats = risk_engine.calculate_trust_score(
        forensics_report, all_detections, is_child, pii, barcodes, meta_report
    )

    # --- REPORTING PHASE ---
    print("\n" + "="*40)
    print(f" GUARDIAN AI REPORT ")
    print("="*40)
    print(f"TRUST SCORE: {score}/100")
    print(f"STATUS: {'[HIGH RISK]' if score < 50 else '[SAFE]'}")
    print("-" * 20)
    print("THREATS DETECTED:")
    for t in threats:
        print(f"[!] {t}")
    
    print("-" * 20)
    print(f"Faces Found: {len(faces)}")
    print(f"Barcodes Found: {len(barcodes)}")
    print("="*40 + "\n")

    # --- INTERACTION PHASE ---
    print("Generating Preview Map...")
    
    # 1. Create a map so the user knows which Face is ID #0, #1, etc.
    preview_img = protector.generate_preview(image, all_detections)
    preview_path = save_image_safe(preview_img, args.image, "_preview_map")
    
    print(f"[*] CHECK THIS IMAGE: {preview_path}")
    print("[*] It has green boxes with ID numbers on it.")
    print("-" * 40)
    
    print("Choose Protection Action:")
    print("[1] Blur SPECIFIC Faces/Items")
    print("[2] Blur ALL Detected Items")
    print("[3] Cloak Faces (Anti-AI Noise)")
    print("[4] Exit")
    
    choice = input("Select [1-4]: ")

    if choice == '1':
        # Selective Redaction
        print("\nEnter the IDs you want to blur (from the preview image).")
        user_input = input("IDs (separated by comma, e.g., 0, 2): ")
        
        try:
            # Convert string "0, 2" into list of integers [0, 2]
            selected_indices = [int(x.strip()) for x in user_input.split(',')]
            
            # Filter the main list to only include what the user picked
            items_to_blur = []
            for idx in selected_indices:
                if 0 <= idx < len(all_detections):
                    items_to_blur.append(all_detections[idx])
                else:
                    print(f"[!] Warning: ID {idx} is invalid, skipping.")
            
            if items_to_blur:
                protected_img = protector.smart_redact(image, items_to_blur)
                saved_path = save_image_safe(protected_img, args.image, Config.SAFE_SUFFIX)
                print(f"[*] Selective blur applied. Saved to: {saved_path}")
            else:
                print("[!] No valid IDs selected.")
                
        except ValueError:
            print("[!] Invalid input format. Use numbers separated by commas.")

    elif choice == '2':
        # Blur Everything
        protected_img = protector.smart_redact(image, all_detections)
        saved_path = save_image_safe(protected_img, args.image, Config.SAFE_SUFFIX)
        print(f"[*] All items redacted. Saved to: {saved_path}")
        
    elif choice == '3':
        # Cloaking
        for face in faces:
            protected_img = protector.cloak_face(image, face['box'])
        saved_path = save_image_safe(image, args.image, "_cloaked")
        print(f"[*] Cloaked image saved to: {saved_path}")
        
    else:
        print("[*] Exiting without changes.")
        # Clean up the preview file so it doesn't clutter the folder
        if os.path.exists(preview_path):
            os.remove(preview_path)

if __name__ == "__main__":
    main()