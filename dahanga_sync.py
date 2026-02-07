import ee
import os
import json
from datetime import datetime, timedelta

def run_dahanga_monitoring():
    # 1. Authenticate using the secret passed from YAML
    try:
        # This matches the env variable in your YAML
        json_text = os.environ.get('GEE_JSON_KEY')
        gee_json_key = json.loads(json_text)
        
        credentials = ee.ServiceAccountCredentials(
            gee_json_key['client_email'], 
            key_data=json_text
        )
        # Using your new project ID 'dahanga'
        ee.Initialize(credentials, project='dahanga')
        print("Connected to GEE Project: Dahanga")
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    # 2. Set the Region (Gahanga Sector)
    asset_path = "projects/dahanga/assets/Gahanga_Sector"
    gahanga_aoi = ee.FeatureCollection(asset_path)
    region = gahanga_aoi.geometry().bounds()

    # 3. Check for the Latest Image
    # Search the last 10 days for a fresh Sentinel-2 photo
    now = datetime.now()
    s2_col = ee.ImageCollection("COPERNICUS/S2_HARMONIZED") \
               .filterBounds(region) \
               .filterDate((now - timedelta(days=10)).strftime('%Y-%m-%d'), now.strftime('%Y-%m-%d')) \
               .sort('system:time_start', False)
    
    latest_img = s2_col.first()

    if latest_img.getInfo():
        img_id = latest_img.id().getInfo()
        print(f"Latest Image Found: {img_id}")

        # 4. Export Task (Visual Check for Work #1)
        task_name = f"Gahanga_Check_{now.strftime('%H%M')}"
        
        task = ee.batch.Export.image.toAsset(
            image=latest_img.select(['B4', 'B3', 'B2']).divide(10000),
            description=task_name,
            assetId=f"projects/dahanga/assets/{task_name}",
            scale=10, 
            region=region,
            maxPixels=1e8
        )
        task.start()
        print(f"Success! Task '{task_name}' is now running in your GEE Task tab.")
    else:
        print("No recent images found for Gahanga. Robot is going back to sleep.")

if __name__ == "__main__":
    run_dahanga_monitoring()
