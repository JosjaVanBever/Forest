#!/bin/bash
#PBS -N NAME
# send mail when aborted (a) or ended (e):
#PBS -m a
# #PBS -q short
#PBS -l walltime=WALLTIME
#PBS -l nodes=1:ppn=3

# avoid any short of memory:
ulimit -s unlimited
# load the appropriate modules:

# standard output ends in home
cd "${PBS_O_WORKDIR}"

exit 0

