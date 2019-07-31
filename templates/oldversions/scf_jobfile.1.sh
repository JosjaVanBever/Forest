#!/bin/bash
#PBS -N scf_RELATIV_R_TYPE
# send mail when aborted or ended:
#PBS -m ae
# WARNING: conda is compiled on victini and therefor
# has to be used only on victini or skitty
# #PBS -q short
#PBS -l walltime=WALLTIME
#PBS -l nodes=1:ppn=3

# avoid any short of memory:
ulimit -s unlimited
# load the appropriate modules:
. ${VSC_SCRATCH_KYUKON_VO}/vsc42800/miniconda3/etc/profile.d/conda.sh
conda activate p4dev

# standard output ends in home
cd "${PBS_O_WORKDIR}"
#WORKINGSPACE=CrF6/RELATIV/BASIS/ACTIVESPACE/R
#cd $WORKINGSPACE/scf
psi4 -n3 scf_in.dat scf_out.dat

exit 0

