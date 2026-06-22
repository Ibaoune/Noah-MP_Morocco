#!/bin/bash
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/forcing/MERRA2
for var in M2T1NXFLX M2T1NXRAD M2T1NXSLV; do
  if [ -d "$var" ]; then
    echo "Processing $var..."
    for file in $var/*.nc4; do
      [ -e "$file" ] || continue
      filename=$(basename $file)
      date_str=$(echo $filename | grep -oE '[0-9]{8}')
      yyyy=${date_str:0:4}
      mm=${date_str:4:2}
      
      target_dir="MERRA2_400/Y${yyyy}/M${mm}"
      mkdir -p $target_dir
      ln -sf ../../../../$var/$filename $target_dir/$filename
    done
  fi
done
echo "Done symlinking."
