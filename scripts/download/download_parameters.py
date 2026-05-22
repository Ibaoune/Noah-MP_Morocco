#!/usr/bin/env python3
import os
import requests
import sys

BASE_URL = "https://portal.nccs.nasa.gov/lisdata_pub/data/PARAMETERS"
OUT_DIR = "input"

# Ensure directories exist
os.makedirs(f"{OUT_DIR}/noah_2dparms", exist_ok=True)
os.makedirs(f"{OUT_DIR}/topo_parms/GTOPO30", exist_ok=True)

files_to_download = [
    # Topography
    ("topo_parms/GTOPO30_native/w020n40.tar.gz", "topo_parms/GTOPO30/w020n40.tar.gz"),
    # Noah 2D Parameters
    ("noah_2dparms/igbp.bin", "noah_2dparms/igbp.bin"),
    ("noah_2dparms/topsoil30snew", "noah_2dparms/topsoil30snew"),
    ("noah_2dparms/islope", "noah_2dparms/islope"),
    ("noah_2dparms/maximum_snow_albedo.hdf", "noah_2dparms/maximum_snow_albedo.hdf"),
    ("noah_2dparms/SOILTEMP.60", "noah_2dparms/SOILTEMP.60"),
    ("noah_2dparms/albedo", "noah_2dparms/albedo"),
    ("noah_2dparms/maxsnoalb.asc", "noah_2dparms/maxsnoalb.asc"),
    ("noah_2dparms/gfrac_min.asc", "noah_2dparms/gfrac_min.asc"),
    ("noah_2dparms/gfrac_max.asc", "noah_2dparms/gfrac_max.asc"),
    ("noah_2dparms/gfrac_min_mon.asc", "noah_2dparms/gfrac_min_mon.asc"),
    ("noah_2dparms/gfrac_max_mon.asc", "noah_2dparms/gfrac_max_mon.asc"),
]

# Add monthly albedo and greenness files
months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
for m in months:
    files_to_download.append((f"noah_2dparms/albedo_{m}.asc", f"noah_2dparms/albedo_{m}.asc"))
    files_to_download.append((f"noah_2dparms/gfrac_{m}.asc", f"noah_2dparms/gfrac_{m}.asc"))

def download_file(src_rel_path, dest_rel_path):
    url = f"{BASE_URL}/{src_rel_path}"
    dest_path = f"{OUT_DIR}/{dest_rel_path}"
    
    if os.path.exists(dest_path):
        # Quick size check
        try:
            r = requests.head(url, verify=True)
            remote_size = int(r.headers.get('content-length', 0))
            local_size = os.path.getsize(dest_path)
            if remote_size == local_size and local_size > 0:
                print(f"[SKIP] Already downloaded: {dest_rel_path}")
                return
        except Exception:
            pass
            
    print(f"[DOWNLOADING] {url} -> {dest_path}")
    with requests.get(url, stream=True, verify=True) as r:
        r.raise_for_status()
        total_length = int(r.headers.get('content-length', 0))
        dl = 0
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    dl += len(chunk)
                    if total_length > 0 and dl % (8192*100) == 0:
                        percent = 100 * dl / total_length
                        sys.stdout.write(f"\rProgress: {percent:.1f}% ({dl/(1024*1024):.1f} MB / {total_length/(1024*1024):.1f} MB)")
                        sys.stdout.flush()
    sys.stdout.write("\n")
    print(f"[COMPLETE] {dest_rel_path}")

if __name__ == "__main__":
    print("Starting LIS static parameters download...")
    for src, dest in files_to_download:
        try:
            download_file(src, dest)
        except Exception as e:
            print(f"[ERROR] Failed to download {src}: {e}", file=sys.stderr)
    
    # Extract GTOPO30 tile
    gtopo_tar = f"{OUT_DIR}/topo_parms/GTOPO30/w020n40.tar.gz"
    gtopo_dir = f"{OUT_DIR}/topo_parms/GTOPO30/w020n40"
    os.makedirs(gtopo_dir, exist_ok=True)
    if os.path.exists(gtopo_tar) and not os.listdir(gtopo_dir):
        print(f"Extracting GTOPO30 tile: {gtopo_tar} -> {gtopo_dir}")
        os.system(f"tar -xf {gtopo_tar} -C {gtopo_dir}")
        print("Extraction complete.")
    
    print("All LIS parameters downloaded and ready.")
