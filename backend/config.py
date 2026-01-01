class Config:
    """
    Central configuration file.
    Think of this like the 'Settings' menu in a video game.
    """
    
    # --- RISK WEIGHTS (How much points we lose for bad things) ---
    # We start with a score of 100. These are the penalties.
    WEIGHT_DEEPFAKE = 50       # High penalty: Fake images are dangerous.
    WEIGHT_GPS = 40            # High penalty: Knowing where you live is risky.
    WEIGHT_CHILD = 30          # Medium penalty: Sharing kids photos is risky ("Sharenting").
    WEIGHT_BARCODE = 20        # Low penalty: Might reveal tickets or receipts.
    WEIGHT_PII = 15            # Low penalty: Email addresses or phone numbers.

    # --- SENSITIVITY THRESHOLDS (How strict the detectors are) ---
    
    # ELA (Error Level Analysis) Sensitivity:
    # When we compress an image, how much "noise" difference do we allow?
    ELA_FACTOR = 10            # Multiplier to make invisible noise visible.
    
    # Face Detection:
    # 0.0 to 1.0. Higher means we only detect faces we are super sure about.
    FACE_CONFIDENCE = 0.5      
    
    # Child Logic:
    # If a face takes up more than 20% of the image height, we assume it's a "Subject" (potential child).
    FACE_SIZE_RATIO = 0.20     
    
    # File Paths (For saving safe versions)
    SAFE_SUFFIX = "_guardian_safe"