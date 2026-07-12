#!/usr/bin/env python3
import os
import sys
import yaml
import argparse
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime

import ee
import geemap

POSTPROC_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = POSTPROC_DIR.parent.parent
CONFIG_PATH = POSTPROC_DIR / "configs" / "observations" / "wapor_v2_aeti.yaml"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Fallback bounding box for NorthMor
BBOX = [-18.0, 20.0, 0.0, 36.0]

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Download WaPOR v2 AETI dekadal data")
    parser.add_argument("--config", type=str, default=str(CONFIG_PATH), help="Path to config file")
    parser.add_argument("--dry-run", action="store_true", help="Print operations without executing")
    parser.add_argument("--verify-only", action="store_true", help="Check existing files and build manifest")
    args = parser.parse_args()

    config = load_config(args.config)
    
    raw_rel_path = config.get("local_paths", {}).get("raw", "data/validation/evapotranspiration/WaPOR/WaPOR_v2_AETI/raw/2016/")
    raw_dir = PROJECT_ROOT / raw_rel_path
    meta_dir = raw_dir.parent.parent / "metadata"
    
    if not args.dry_run:
        raw_dir.mkdir(parents=True, exist_ok=True)
        meta_dir.mkdir(parents=True, exist_ok=True)
        
    try:
        ee.Initialize()
    except Exception as e:
        logger.error(f"Google Earth Engine init failed: {e}")
        sys.exit(1)
        
    roi = ee.Geometry.Rectangle(BBOX)
    
    # In WaPOR v2 GEE, the ID is FAO/WAPOR/2/L1_AETI_D
    collection_id = "FAO/WAPOR/2/L1_AETI_D"
    
    logger.info(f"Target Collection: {collection_id}")
    logger.info(f"Target Year: 2016")
    
    start_date = "2016-01-01"
    end_date = "2016-12-31"
    
    collection = ee.ImageCollection(collection_id).filterDate(start_date, end_date).filterBounds(roi)
    
    try:
        image_list = collection.toList(collection.size())
        num_images = image_list.size().getInfo()
    except Exception as e:
        logger.error(f"Failed to fetch collection info: {e}")
        sys.exit(1)
        
    logger.info(f"Found {num_images} images in GEE for 2016.")
    
    if num_images != 36:
        logger.warning(f"Expected 36 dekades, but found {num_images}!")
        
    downloaded_files = []
    
    for i in range(num_images):
        img = ee.Image(image_list.get(i))
        info = img.getInfo()
        
        # 'L1_AETI_1601' or similar ID
        img_id = info['id'].split('/')[-1]
        
        out_file = raw_dir / f"{img_id}.tif"
        
        if out_file.exists():
            if not args.dry_run:
                logger.info(f"  ✓ Already exists: {out_file.name}")
            downloaded_files.append({"filename": out_file.name, "path": str(out_file), "status": "EXISTING"})
            continue
            
        if args.verify_only:
            logger.error(f"  ✗ Missing file: {out_file.name}")
            downloaded_files.append({"filename": out_file.name, "path": str(out_file), "status": "MISSING"})
            continue
            
        if args.dry_run:
            logger.info(f"  (Dry-Run) Would download {img_id}.tif")
            continue
            
        logger.info(f"  ↓ Downloading {img_id} ...")
        try:
            geemap.download_ee_image(
                img.clip(roi), 
                filename=str(out_file), 
                scale=250, 
                region=roi, 
                crs="EPSG:4326"
            )
            if out_file.exists() and out_file.stat().st_size > 100:
                downloaded_files.append({"filename": out_file.name, "path": str(out_file), "status": "DOWNLOADED"})
                logger.info(f"  ✓ Downloaded {img_id}.tif")
            else:
                if out_file.exists():
                    out_file.unlink()
                raise Exception("File empty or not created due to GEE limits")
        except Exception as e:
            logger.error(f"  ✗ Failed to download {img_id}: {e}")
            downloaded_files.append({"filename": out_file.name, "path": str(out_file), "status": "FAILED"})

    if args.dry_run:
        return

    # Post-Download checks
    valid_downloads = [f for f in downloaded_files if f["status"] in ["EXISTING", "DOWNLOADED"]]
    
    # Generate Inventory CSV
    df = pd.DataFrame(downloaded_files)
    df.to_csv(meta_dir / "wapor_v2_2016_file_inventory.csv", index=False)
    
    # Basic metadata CSV
    meta_data = []
    for i in range(num_images):
        info = ee.Image(image_list.get(i)).getInfo()
        meta_data.append({
            "id": info['id'].split('/')[-1],
            "start_time": info['properties'].get('system:time_start'),
            "end_time": info['properties'].get('system:time_end'),
        })
    df_meta = pd.DataFrame(meta_data)
    df_meta.to_csv(meta_dir / "wapor_v2_2016_metadata.csv", index=False)
    
    # Generate report
    with open(meta_dir / "wapor_v2_2016_download_report.md", "w") as f:
        f.write("# Rapport d'Acquisition WaPOR v2 AETI (LOT 3A)\n\n")
        f.write(f"- Source : {collection_id} (Google Earth Engine)\n")
        f.write(f"- Fichiers trouvés (GEE) : {num_images}\n")
        f.write(f"- Fichiers téléchargés/existants : {len(valid_downloads)}\n\n")
        
        if len(valid_downloads) == 36:
            status = "DOWNLOAD_COMPLETE_AND_VERIFIED"
        elif len(valid_downloads) > 0:
            status = "DOWNLOAD_COMPLETE_WITH_GAPS"
        else:
            status = "DOWNLOAD_FAILED"
            
        f.write(f"**STATUS FINAL : {status}**\n")

    manifest = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "files_count": len(valid_downloads)
    }
    with open(meta_dir / "wapor_v2_2016_download_manifest.yaml", "w") as f:
        yaml.dump(manifest, f)
        
    logger.info(f"LOT 3A Download Process Finished. Status: {status}")

if __name__ == "__main__":
    main()
