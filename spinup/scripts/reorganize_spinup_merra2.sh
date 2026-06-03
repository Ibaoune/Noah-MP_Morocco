#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
# Script to reorganize MERRA2 files for the 2015-2020 Spin-Up
# LIS expects: <base>/MERRA2_400/Y<YYYY>/M<MM>/<filename>

BASE="data/met_forcing/MERRA2"

echo "Reorganizing MERRA-2 files for 2015-2020..."

for year in {2015..2020}; do
  for month in 01 02 03 04 05 06 07 08 09 10 11 12; do
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

# Create Dec 31 2014 placeholder (LIS needs day before start date for interpolation)
echo "Creating 2014-12-31 placeholder using 2015-01-01 data..."
mkdir -p "${BASE}/MERRA2_400/Y2014/M12"
for spec in flx slv rad; do
  src="${BASE}/MERRA2_400/Y2015/M01/MERRA2_400.tavg1_2d_${spec}_Nx.20150101.nc4"
  dst="${BASE}/MERRA2_400/Y2014/M12/MERRA2_400.tavg1_2d_${spec}_Nx.20141231.nc4"
  [ -L "$dst" ] || ln -sf "$(realpath $src)" "$dst"
done

echo "MERRA2 directory reorganization complete."
