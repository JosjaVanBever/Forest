#!/bin/bash
#PBS -N chemps2_CrF6_BASIS_RELATIV_R_TYPE
# send mail when aborted or ended:
#PBS -m ae
#PBS -q QUEUE
#PBS -l walltime=WALLTIME
#PBS -l nodes=1:ppn=RESOURCES

# avoid any short of memory:
ulimit -s unlimited
# load the appropriate modules:
module load CheMPS2
# necessary for activating openmpi
# MULTIPLE NODES
# module load vsc-mympirun

# standard output ends in home
cd "${PBS_O_WORKDIR}"/DMRGSUBDIR
MP_NUM_THREADS="${PBS_NUM_PPN}" chemps2 --file=dmrg.in &> dmrg.out
# mv "${PBS_O_WORKDIR}"/scf/scf.molden.rotated .

exit 0

