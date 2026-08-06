#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

JOB_ID=7309585
while squeue -u mohammad.elaabaribao | grep -q ${JOB_ID}; do
    sleep 10
done
./collect_review.sh > collect.log 2>&1
echo "DONE" > collect.status
