#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
mkdir -p data/land_params/noahmp401_parms
cd data/land_params/noahmp401_parms
wget -c https://portal.nccs.nasa.gov/lisdata_pub/data/PARAMETERS/noahmp401_parms/SOILPARM.TBL
wget -c https://portal.nccs.nasa.gov/lisdata_pub/data/PARAMETERS/noahmp401_parms/GENPARM.TBL
wget -c https://portal.nccs.nasa.gov/lisdata_pub/data/PARAMETERS/noahmp401_parms/MPTABLE.TBL
wget -c https://portal.nccs.nasa.gov/lisdata_pub/data/PARAMETERS/noahmp401_parms/VEGPARM.TBL
cd ../../../
