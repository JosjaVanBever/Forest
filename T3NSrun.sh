#!/bin/bash

if [ "x${cont}" != "x" ]; then
    cont="--continue=${cont}"
fi
if [ "x${inputf}" == "x" ]; then
    inputf="template.in"
fi

# NAME="${inputf%\.in}${PBS_JOBID%%\.*}"
OUTPFILE="${PBS_JOBNAME##.*\/}${PBS_JOBID%%\.*}.out"

### Modules
# module load HDF5 CMake
module load HDF5/1.10.2-intel-2018b CMake/3.12.1-GCCcore-7.3.0
# module load HDF5/1.10.2-intel-2018b CMake/3.9.6
if [ $? -ne 0 ]; then
    echo "Error loading modules" 1>&2
    exit 1
fi

COMPILER=$(which icc)
if [ "x$COMPILER" = "x" -o $? -ne 0 ]; then
    echo "Error loading the compiler" 1>&2
    exit 1
fi

### Directories
export T3NSDir=$VSC_HOME/scratch/T3NS
export tempdir=${TMPDIR:=.}/tmp$PBS_JOBID
# export tempdir=${PBS_O_WORKDIR:=.}/tmp$PBS_JOBID

echo $T3NSDir
echo $tempdir

### go to temporary directory
cd ${PBS_O_WORKDIR:=.}
mkdir -p $tempdir/T3NS
cd $tempdir

### create T3NS binary if necessary
if [ -z "${binary}" ]
then
    cp -r $T3NSDir .
    cd T3NS
    rm -rf build
    mkdir build
    cd build
    
    CC=$COMPILER cmake -DMKL=ON ..
    if [ $? -ne 0 ]; then
        echo "Error in CMake" 1>&2
        rm -rf $tempdir
        exit 1
    fi
    
    make -j${PBS_NUM_PPN:=1} VERBOSE=1
    if [ $? -ne 0 ]; then
        echo "Error in make" 1>&2
        rm -rf $tempdir
        exit 1
    fi
    export T3NSbin="$PWD/src/T3NS"
    ls $T3NSbin > /dev/null
    if [ $? -ne 0 ]; then
        echo "No T3NS binary found at $T3NSbin" 1>&2
        rm -rf $tempdir
        exit 1
    fi
else
  export T3NSbin="${binary}"
fi

### Calculations
cd $PBS_O_WORKDIR
OMP_NUM_THREADS=$PBS_NUM_PPN $T3NSbin ${cont} ${inputf} > $OUTPFILE

### Clean tempdir
rm -rf $tempdir

# print stop time
date

exit 0
