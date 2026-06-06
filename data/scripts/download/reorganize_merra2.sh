#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

# Script to reorganize MERRA2 files into LIS-expected directory structure
# LIS expects: <base>/MERRA2_400/Y<YYYY>/M<MM>/<filename>
# Downloaded data is in: <base>/M2T1NXFLX/ and M2T1NXSLV/ and M2T1NXRAD/

BASE="input/MET_FORCING/MERRA2"

for year in 2020; do
  for month in 06 07 08; do
    mkdir -p "${BASE}/MERRA2_400/Y${year}/M${month}"
    for coll in FLX SLV RAD; do
      spec="flx"
      [ "$coll" = "SLV" ] && spec="slv"
      [ "$coll" = "RAD" ] && spec="rad"
      for f in ${BASE}/M2T1NX${coll}/MERRA2_400.tavg1_2d_${spec}_Nx.${year}${month}*.nc4; do
        [ -f "$f" ] || continue
        base=$(basename "$f")
        ln -sf "$(realpath $f)" "${BASE}/MERRA2_400/Y${year}/M${month}/${base}"
      done
    done
  done
done

# Create May 31 placeholder (LIS needs day before start date for interpolation)
mkdir -p "${BASE}/MERRA2_400/Y2020/M05"
for spec in flx slv rad; do
  src="${BASE}/MERRA2_400/Y2020/M06/MERRA2_400.tavg1_2d_${spec}_Nx.20200601.nc4"
  dst="${BASE}/MERRA2_400/Y2020/M05/MERRA2_400.tavg1_2d_${spec}_Nx.20200531.nc4"
  [ -L "$dst" ] || ln -sf "$(realpath $src)" "$dst"
done

echo "MERRA2 directory reorganization complete."
echo "Structure:"
for m in M05 M06 M07 M08; do
  count=$(ls "${BASE}/MERRA2_400/Y2020/${m}/" 2>/dev/null | wc -l)
  echo "  Y2020/${m}: $count files"
done
