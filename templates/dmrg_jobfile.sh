#!/bin/bash
#PBS -N chemps2_CrF6_BASIS_REL_R_TYPE
#PBS -m ae
#PBS -q QUEUE
#PBS -l walltime=WALLTIME
#PBS -l nodes=1:ppn=RESOURCES

# -m : send mail when aborted or ended:

# load the appropriate modules:
module load CheMPS2

# MULTIPLE NODES
# necessary for activating openmpi
# module load vsc-mympirun

# standard output ends in home
cd "${PBS_O_WORKDIR}"/DMRGSUBDIR
MP_NUM_THREADS="${PBS_NUM_PPN}" chemps2 --file=dmrg.in &> dmrg.out
# mv "${PBS_O_WORKDIR}"/scf/scf.molden.rotated .

exit 0

