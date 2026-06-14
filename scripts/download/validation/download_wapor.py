import argparse
import os
import sys
import ee
import geemap
import logging
from config_validation import DIR_WAPOR, DOMAIN_BBOX

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Map components to GEE collections
GEE_COLLECTIONS = {
    "AETI": "projects/UNFAO/wapor/v3/L1-AETI-D",
    "E": "projects/UNFAO/wapor/v3/L1-E-D",
    "T": "projects/UNFAO/wapor/v3/L1-T-D",
    "NPP": "projects/UNFAO/wapor/v3/L1-NPP-D",
}

def main():
    parser = argparse.ArgumentParser(description="Download WaPOR v3 data via Google Earth Engine.")
    parser.add_argument("--start_date", type=str, default="2015-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2020-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--components", type=str, nargs="+", choices=["AETI", "T", "E", "NPP"], required=True)
    parser.add_argument("--level", type=str, default="L1", help="Ignored in GEE script, defaults to L1.")
    args = parser.parse_args()

    # Initialize Earth Engine
    try:
        ee.Initialize(project='ee-mohammadelaabaribao') # Will fallback to default if project is none
    except Exception as e:
        try:
            ee.Initialize()
        except Exception as e:
            logger.error("Earth Engine is not authenticated. Please run 'earthengine authenticate' first.")
            logger.error(str(e))
            sys.exit(1)

    # Define region of interest
    min_lon, min_lat, max_lon, max_lat = DOMAIN_BBOX
    roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

    # Convert dates to years
    start_year = int(args.start_date.split("-")[0])
    end_year = int(args.end_date.split("-")[0])

    for comp in args.components:
        collection_id = GEE_COLLECTIONS[comp]
        logger.info(f"Processing component {comp} from {collection_id} ...")
        
        # Create output directory
        out_dir = os.path.join(DIR_WAPOR, f"WaPOR_v3_{comp}")
        os.makedirs(out_dir, exist_ok=True)
        
        # Load collection
        collection = ee.ImageCollection(collection_id)
        
        for year in range(start_year, end_year + 1):
            out_file = os.path.join(out_dir, f"WaPOR_v3_{comp}_{year}.tif")
            if os.path.exists(out_file):
                logger.info(f"  ✓ Already exists: {out_file}")
                continue
                
            logger.info(f"  ↓ Downloading {comp} for {year} ...")
            try:
                # Filter by year and bounds
                yearly_col = collection.filterDate(f"{year}-01-01", f"{year+1}-01-01").filterBounds(roi)
                
                # Check if collection is empty for this year
                num_images = yearly_col.size().getInfo()
                if num_images == 0:
                    logger.warning(f"  ⚠ No data found for {comp} in {year}. Skipping.")
                    continue
                logger.info(f"      Aggregating {num_images} images into annual sum composite...")
                
                # Create annual composite (sum)
                img = yearly_col.sum().clip(roi)
                
                # Export locally directly to the cluster
                # scale=250 meters for L1 WaPOR
                geemap.ee_export_image(
                    img, 
                    filename=out_file, 
                    scale=250, 
                    region=roi, 
                    file_per_band=False
                )
                logger.info(f"  ✓ Saved to {out_file}")
            except Exception as e:
                logger.error(f"  ✗ Failed to download {comp} for {year}: {e}")

if __name__ == "__main__":
    main()
