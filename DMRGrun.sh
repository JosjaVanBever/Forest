#!/bin/bash

# load the appropriate modules:
module load CheMPS2

# extra preparation when using multiple nodes
NR_NODES=$(cat ${PBS_NODEFILE} | uniq | wc -l)
if [ "${NR_NODES}" -gt '1' ]
then
  # necessary for activating openmpi
  module load vsc-mympirun
fi

# start time
date

# standard output ends in home
cd "${PBS_O_WORKDIR}"
# create unique input and link to tmp space
CHEMPS_NAME="${inputf%\.in}${PBS_JOBID%%\.*}"
sed "s|TMPDIR|${TMPDIR}|" "${inputf}" > "${CHEMPS_NAME}.in"
# do the actual job
MP_NUM_THREADS="${PBS_NUM_PPN}" chemps2 --file="${CHEMPS_NAME}.in" &> "${CHEMPS_NAME}.out"
# remove the tmp jobinput
rm "${CHEMPS_NAME}.in"

# mv "${PBS_O_WORKDIR}"/scf/scf.molden.rotated .

# stop time
date

exit 0

