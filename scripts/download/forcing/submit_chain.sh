#!/bin/bash
LAST_JOB=""
for (( year=2017; year>=2000; year-- )); do
    # Submit MERRA-2
    if [ -z "$LAST_JOB" ]; then
        MERRA_JOB=$(sbatch --export=ALL,YEAR=$year --array=1-12 --parsable job_download_merra2.sh)
    else
        MERRA_JOB=$(sbatch --dependency=afterok:$LAST_JOB --export=ALL,YEAR=$year --array=1-12 --parsable job_download_merra2.sh)
    fi
    echo "Submitted MERRA-2 $year with JOB_ID: $MERRA_JOB"
    
    # Submit IMERG
    IMERG_JOB=$(sbatch --dependency=afterok:$MERRA_JOB --export=ALL,YEAR=$year --array=1-12 --parsable job_download_imerg.sh)
    echo "Submitted IMERG $year with JOB_ID: $IMERG_JOB"
    
    LAST_JOB=$IMERG_JOB
done
echo "All jobs queued sequentially!"
