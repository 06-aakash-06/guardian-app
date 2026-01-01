from config import Config

class RiskEngine:
    def calculate_trust_score(self, forensics, content_detections, is_child, pii_list, barcodes, metadata):
        """
        Calculates a score from 0 (Dangerous) to 100 (Safe).
        It's like a reverse test score: you start with 100 and lose points for mistakes.
        """
        score = 100
        threats = []

        # 1. Check Forensics (Deepfakes/Photoshop)
        if forensics['ela_manipulated']:
            score -= Config.WEIGHT_DEEPFAKE
            threats.append("Possible Digital Manipulation (Deepfake/Photoshop)")

        # 2. Check GPS (Location Tracking)
        if metadata['gps_found']:
            score -= Config.WEIGHT_GPS
            threats.append("GPS Location Data Embedded")

        # 3. Check Visual Content (Children)
        if is_child:
            score -= Config.WEIGHT_CHILD
            threats.append("Potential Child Detected (Sharenting Risk)")
        
        # 4. Check Barcodes
        if len(barcodes) > 0:
            score -= Config.WEIGHT_BARCODE
            threats.append(f"Found {len(barcodes)} Barcodes/QR Codes")

        # 5. Check PII (Text)
        if len(pii_list) > 0:
            score -= Config.WEIGHT_PII
            threats.append(f"Personal Text Found: {', '.join(pii_list)}")

        # 6. CRITICAL CONTEXT LOGIC
        # If we have GPS coordinates AND a Child in the photo, the risk is maximum.
        # This is because predators could locate the child.
        if metadata['gps_found'] and is_child:
            score = 0
            threats.append("CRITICAL: Child Face + GPS Location combined!")

        # Ensure score doesn't go below 0
        return max(score, 0), threats