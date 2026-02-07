import ee
import os
import json
import base64
from datetime import datetime, timedelta

def run_dahanga_monitoring():
    # 1. Fetch the secret from the environment
    encoded_key = os.environ.get('GEE_JSON_KEY')
    
    if not encoded_key:
        print("❌ ERROR: Secret not found! Check if 'DAHA_REPO_SEC' is set in GitHub.")
        return

    try:
        # 2. Decode the Base64 Key
        decoded_bytes = base64.b64decode(encoded_key)
        gee_json_key = json.loads(decoded_bytes.decode('utf-8'))
        
        # 3. Authenticate to the 'dahanga' project
        credentials = ee.ServiceAccountCredentials(
            gee_json_key['client_email'], 
            key_data=json.dumps(gee_json_key)
        )
        ee.Initialize(credentials, project='dahanga')
        print("✅ SUCCESS: Connected to Project Dahanga.")
        
    except Exception as e:
        print(f"❌ AUTH ERROR: {e}")
        return

    # 4. Define Region (Gahanga Sector)
    # Ensure this asset 'Gahanga_Sector' has finished its upload (turned Green)
    try:
        gahanga_aoi = ee.FeatureCollection("projects/dahanga/assets/Gahanga_Sector")
        
        # Simple verification task
        img = ee.ImageCollection("COPERNICUS/S2_HARMONIZED") \
                .filterBounds(gahanga_aoi) \
                .sort('system:time_start', False).first()

        if img.getInfo():
            task_id = f"Gahanga_Verif_{datetime.now().strftime('%H%M')}"
            task = ee.batch.Export.image.toAsset(
                image=img.select(['B4', 'B3', 'B2']).divide(10000),
                description=task_id,
                assetId=f"projects/dahanga/assets/{task_id}",
                scale=10,
                region=gahanga_aoi.geometry().bounds()
            )
            task.start()
            print(f"🚀 Task started: {task_id}. Check GEE Tasks tab!")
    except Exception as e:
        print(f"❌ ASSET ERROR: Could not find Gahanga_Sector. Is it still uploading? {e}")

if __name__ == "__main__":
    run_dahanga_monitoring()
