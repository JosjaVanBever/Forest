#!/bin/bash
#PBS -N scf_REL_R
#PBS -l walltime=WALLTIME
#PBS -l nodes=1:ppn=3
#PBS -m a
## #PBS -q short

# -m : send mail when aborted (a) or ended (e):
# -q short: WARNING: conda is compiled on victini and therefore
#           has to be used only on victini or skitty

# load the appropriate modules:
. ${VSC_SCRATCH_KYUKON_VO}/vsc42800/miniconda3/etc/profile.d/conda.sh
conda activate p4dev

# standard output ends in home
cd "${PBS_O_WORKDIR}"
psi4 -n3 scf_in.dat scf_out.dat

cd ..
bash jobs.sh

exit 0

