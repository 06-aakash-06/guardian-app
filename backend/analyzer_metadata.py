from PIL import Image, ExifTags

class AnalyzerMetadata:
    def get_metadata_risk(self, image_path: str):
        """
        Extracts EXIF data. This is hidden data cameras write into the file.
        It usually contains Date, Camera Model, and sometimes GPS location.
        """
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        risk_report = {
            "gps_found": False,
            "device_info": "Unknown (Stripped?)",
            "lat": None,
            "lon": None
        }

        if not exif_data:
            return risk_report # No metadata found (Safe but suspicious)

        # 1. Map the cryptic number codes (e.g., 34853) to human names (e.g., GPSInfo).
        for tag_id, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)

            if tag_name == 'GPSInfo':
                # GPS is found! This is a major privacy risk.
                risk_report["gps_found"] = True
            
            if tag_name == 'Make' or tag_name == 'Model':
                risk_report["device_info"] = str(value)

        return risk_report