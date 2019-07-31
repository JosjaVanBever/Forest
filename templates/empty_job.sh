#!/bin/bash
#PBS -N NAME
#PBS -m a
#PBS -l walltime=WALLTIME
#PBS -l nodes=1:ppn=3
# #PBS -q short

# -m : send mail when aborted (a) or ended (e)
# -q short : not all queues are available
#            on all clusters

# load the appropriate modules:

# standard output ends in home
cd "${PBS_O_WORKDIR}"

exit 0

