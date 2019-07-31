bin/
Contains scripts to manage in-/output files:
--------------------------------------------

modules.sh : load the appropriate modules 
usage: . modules.sh

create_sample : create a directory with scf/, dmrg/ and t3ns/
usage: create_sample NAME

psi4_input : create the input file for a psi4 run
examples: psi4_input scf energy cc-pVDZ ${CRFBIN}/templates/geom_CrF6.xyz
          psi4_input scf energy ano-rcc_restricted ${CRFBIN}/templates/geom_CrF6.xyz dkh

fcimanip : creates a new FCIDUMP file with specified active space
usage: fcimanip ./scf.FCIDUMP ./act.FCIDUMP ./orborder.txt
REMARK: python 2 needed!

fciformat : format the FCIDUMP file to be readable by chemps2. This includes
a convertion of irrep convention and header format
example: fciformat scf.FCIDUMP D2h > scfMol.FCIDUMP

plant.py : create a tree using a seed
usage : python $CRFBIN/plant.py FCIDUMP SEED

DMRGrun.sh : perform a dmrg calculation
usage on this node : inputf=dmrg.in bash $CRFBIN/DMRGrun.sh
usage by qsub : qsub -N jobname -l walltime=hh:mm:ss,nodes=x:ppn=y -v inputf=dmrg.in $CRFBIN/DMRGrun.sh 
T3NSrun.sh : perform a t3ns calculation
usage on this node : inputf=t3ns.in,cont=T3NScalc.h5 bash $CRFBIN/T3NSrun.sh
usage by qsub examples : (1) qsub -N jobname -l walltime=24:00:00,nodes=1:ppn=36,mem=85gb,vmem=85gb -v inputf=t3ns.in,cont=T3NScalc.h5 $CRFBIN/T3NSrun.sh
                         (2) qsub -N jobname -l walltime=00:06:00,nodes=1:ppn=2  -v inputf=t3ns.in,cont=T3NScalc.h5,binary=$T3NSBUILD/skitty/src/T3NS $CRFBIN/T3NSrun.sh

dmrgScan : qsub multiple dmrg calculations using filters
usage example : dmrgScan -t -f '1.732 1.734' -f '33Ohact 33D2hact' -f 'Ag1 Ag2' -l walltime=72:00:00,nodes=1:ppn=36 skitty
t3nsScan : qsub multiple t3ns calculations using filters
usage example : t3nsScan -t -f '1.732 1.734' -f '33Ohact 33D2hact' -f 'Ag1 Ag2' -l walltime=72:00:00,nodes=1:ppn=36 skitty
REMARK: -t is used to test the adressed subset; remove this flag to actually submit the jobs

--------------------------------------------------------------------------------------

Deprecated:

fcidump/psi2molcas.py : convert the psi4 irrep numbering to the molpro irrep numbering
usage: python psi2molpro.py xxx.FCIDUMP SYMMGROUP > xxxMol.FCIDUMP
REMARK: python 2 needed!

fcidump/fcidump_new2old : converts an FCIDUMP file from new to old format
usage: fcidump_new2old ./name.FCIDUMP

fcidump/FCImanip.py : creates a new FCIDUMP file with specified active space
REMARK: FCImanip == python $CRFBIN/fcidump/FCImanip.py
usage: FCImanip ./scf.FCIDUMP ./act.FCIDUMP ./orborder.txt
REMARK: python 2 needed!
REMARK: take precaution when dealing with large FCIDUMP files!

--------------------------------------------------------------------------------------

Toolbox:

# filter out the regime energies encountered in a bunch of t3ns calculations
find 1.73? -name *.out | grep t3ns | grep Ag0 | grep -v 18o18e | grep -v 12o12e | xargs grep 'MINIMUM ENERGY ENCOUNTERED :'
# filter out the final energies encountered in a bunch of calculations
find 1.73? -name *.out | grep dmrg | grep Ag0 | xargs grep 'Minimum energy encountered during all instructions'  #| rev | uniq -f2 | rev
# get the E for all subsequent bond dimensions from a dmrg calculation
cat 1.69/dmrg/Ag0/dmrg.out | grep 'Minimum energy encountered during all instructions'
# get the energy to which the scf was converged
cat 1.69/scf/scf_out.dat | grep 'Total Energy ='
# get irreps of active space from orborder file
for i in {1..8}; do echo -n "$i: "; grep "$i:" 33act.D2h.orborder | wc -l; done
# run a bunch of calculations
for r in 1.732 1.734 1.736 1.738; do cd $r/dmrg/; bash jobs.sh 33Ohact golett skitty; cd -; done
# create d3h symmetry input based on sample
for i in [45]*; do cd $i; for j in 1.7*; do sed "s/XXXXX/$j/; s/YYYY/$i/" ../../sample/scf_in.dat > $j/scf_in.dat; done; cd ..; done
for i in [45]*; do cd $i; for j in 1.7*; do sed "s/YYYY_XXXXX/$i\_$j/" ../../sample/jobfile.sh > $j/jobfile.sh; done; cd ..; done

---------------------------------------------------------------------------------------

Interactive jobs:

module swap cluster/pokemon
qstat -q
qsub -I -q short -l walltime=4:00:00 -l nodes=1:ppn=3


Adding arguments to jobs:

qsub jobfile.sh -v param="boe"

---------------------------------------------------------------------------------------

Warnings:

1) Do not use '_' in names of FCIDUMP files.
2) Not all warnings are crashes of chemps2.
e.g. "No file ./Tmp/CheMPS2_eri_temp.h5 found."
is no problem.

