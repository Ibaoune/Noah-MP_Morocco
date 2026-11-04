#!/bin/bash
# Recompilation de LIS (LISF 7.5 standard, HYMAP2 actif, HYMAP v1 inactif)
# Voir experiments/NorthMor/routing/Hymap_troubleshooting.txt, T3.1
#SBATCH --job-name=build_lis_hymap2
#SBATCH --output=experiments/NorthMor/routing/logs/build_lis_hymap2_%j.log
#SBATCH --error=experiments/NorthMor/routing/logs/build_lis_hymap2_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=03:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -e
cd "$SLURM_SUBMIT_DIR"
source arch/arch_toubkal.env
cd src/lisf/lis/make
# Ne pas regenerer Filepath (eviterait l appel vim du Makefile d origine)
for f in user.cfg default.cfg LIS_misc.h; do
  if [ "$f" -nt Filepath ]; then echo "ERREUR: $f plus recent que Filepath"; exit 2; fi
done
grep -n "ROUTE_" LIS_plugins.h
rm -f *.o *.mod *.d LIS
make -j 16 LIS
ls -la LIS
cp -p LIS ../LIS
echo "BUILD OK $(date)"
