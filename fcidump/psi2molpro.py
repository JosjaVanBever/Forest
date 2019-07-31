# -*- coding: utf-8 -*-
# Program to convert the psi4 irrep numbering convention to
# the molcas irrep numbering convention.

import FCIutils as ut
import numpy as np
import sys


# check the arguments
if len(sys.argv) != 3:  # incl. python script
    error_message = 'Syntaxis: python psi2molpro.py ' + \
                    'INPUTFILE SYMMGROUP'
    raise IOError(error_message)

# read in the arguments
psi4file = sys.argv[1]
symmgroup = sys.argv[2]

# the symmetry groups that are supported
symmsupport = ['C1','Ci','C2','Cs','D2','C2v','C2h','D2h']
# the keywords which signals an irrep ordered array
keywords = ['ORBSYM']

# check if the symmetry group is valid
if symmgroup not in symmsupport:
    error_message = 'Symmetry group is not recognized.'
    raise IOError(error_message)

# loop trough the file and print the convertion to stdout
with open(psi4file) as f:
    for line in f:
        line = line.strip('\n')
        irrep_ordered = False
        # if the line contains an irrep ordered array
        for key in keywords:
            if line.startswith(key):
                irrep_ordered = True
                # fromat distinction
                if line.count('=') == 1:
                    sign = '='
                else: sign = ' '
                # actual convertion
                psi4_irreps = map(int, (line.strip(key + ' = ,\n')).split(','))
                molpro_irreps = [ut.psi2mol[symmgroup][psi - 1] + 1 for psi in psi4_irreps]
                sys.stdout.write(key + sign)
                for irrep in molpro_irreps:
                    sys.stdout.write(str(irrep) + ',')
                sys.stdout.write('\n')
        # if the line does not contain an irrep ordered array
        if not irrep_ordered:
            # if the line does not contain any irrep numbering
            print(line)
