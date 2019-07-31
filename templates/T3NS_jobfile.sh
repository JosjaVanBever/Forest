#!/bin/bash
#PBS -N t3ns_REL_RAD_TYP
#PBS -m ae
#PBS -q QUEUE#long
#PBS -l walltime=WALLTIME#24:00:00
#PBS -l nodes=1:ppn=RESOURCES#36

# -m : send mail when aborted or ended:

# do the actual job
bash input=t3ns.in cont=T3NScalc.h5 "${CRFBIN}"/templates/T3NSrun.sh 

exit 0

