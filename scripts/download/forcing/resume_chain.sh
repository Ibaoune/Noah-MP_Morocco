#!/bin/bash

# Start by submitting IMERG 2014 which failed
LAST_JOB=$(sbatch --export=ALL,YEAR=2014 --array=1-12 --parsable job_download_imerg.sh)
echo "Submitted IMERG 2014 with JOB_ID: $LAST_JOB"

# Now chain the rest from 2013 down to 2000
for (( year=2013; year>=2000; year-- )); do
    # Submit MERRA-2
    MERRA_JOB=$(sbatch --dependency=afterok:$LAST_JOB --export=ALL,YEAR=$year --array=1-12 --parsable job_download_merra2.sh)
    echo "Submitted MERRA-2 $year with JOB_ID: $MERRA_JOB"
    
    # Submit IMERG
    IMERG_JOB=$(sbatch --dependency=afterok:$MERRA_JOB --export=ALL,YEAR=$year --array=1-12 --parsable job_download_imerg.sh)
    echo "Submitted IMERG $year with JOB_ID: $IMERG_JOB"
    
    LAST_JOB=$IMERG_JOB
done
echo "All remaining jobs queued sequentially!"
