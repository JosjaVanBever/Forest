# -*- coding: utf-8 -*-
# Program to manipulate the orbital choice and ordering read from
# an FCIDUMP file. The result is written out to a new FCIDUMP file.

import FCIutils as ut
import fcidumpRW as rw
import numpy as np
import sys

# print extra debug info if true
debug = False

# check the arguments
if len(sys.argv) != 3:  # incl. python script
    error_message = 'Syntaxis: python FCIfilter.py INPUTFILE ' + \
                  'ORBORDERFILE'
    raise IOError(error_message)
# try interpreting the argumetns as files
header = sys.argv[1]
orborderfile = sys.argv[2]
# test wether these files can be opened
test = open(sys.argv[1])
test.close()
test = open(sys.argv[2])
test.close()

##### load the header #####
data = rw.load_header(header)

##### collect data from the header #####
# the irrepnbrs of the active orbitals
orbsym = data['orbsym']
# the number of electrons
nelec = data['nelec']
# total spin of the system and type of HF
ms2 = data['ms2']
uhf = data['uhf']


# remark that the indices i, j, k and l loop all the orbitals,
# which are ordered by 1) irrep and 2) energy. E.g. the 5th orbital
# irrep 2 will correspond with index = #(irrep 1) + 5


# the number of irreps and orbitals per irrep
# the orbitals per irrep will be put in a cumulative distribution
n_irrep = orbsym[-1]
irrep_orb =[0 for i in range(n_irrep + 1)]
counter = 1
# calculate the number of orbitals per irrep
for irrep in orbsym:
	counter += 1
	irrep_orb[irrep] += 1
# calculate the cumulative distribution
for i in range (1, len(irrep_orb)):
	irrep_orb[i] += irrep_orb[i-1]

##### read the input orbital ordering #####
# input format irrep:nbr \n irrep:nbr ...
# Remark: numbering starts from 1
#
# occupations per irrep
occupations = []
# numbers of the active orbitals
active_orbs = []
with open(orborderfile) as f:
    for line in f:
        # '#' is preserved for comments
        if not line.startswith('#'):
            if line.startswith('DOCC'):
                occupations = map(int, (line.strip('DOCC []\n')).split(','))
            if line.count(':') == 1:
                irrep, number = line.split(':')
                active_index = irrep_orb[int(irrep) - 1] + int(number)
                # check whether all listed orbitals correspond to the right irrep
                assert(active_index < irrep_orb[int(irrep)] + 1)
                active_orbs.append(active_index)

if len(occupations) == 0:
	raise IOError('Error in orbital ordering file')

# indices of the highest occupied orbitals per irrep (a.k.a. HOMO's)
homos = [irrep_orb[i] + occupations[i] for i in range(n_irrep)]
# indices of the initially occupied orbitals
occupied_inds = []
for i in range(0, n_irrep):
    occupied_inds.extend([j for j in range(irrep_orb[i], irrep_orb[i] + occupations[i])])

if debug:
    # print intermediate results
    print('irrep_orb: ' + str(irrep_orb))
    print('occupations: ' + str(occupations))
    print('occupied_inds: ' + str(occupied_inds))
    print('homos: ' + str(homos))
    print('')


# select the occupied orbitals
core_orbs = []
for i in range(n_irrep):
    core_orbs += range(irrep_orb[i] + 1, homos[i] + 1)
# filter out the occupied orbitals in the active space
core_orbs = list(filter(lambda orb: orb not in active_orbs, core_orbs))

# select the virtual orbitals
virtual_orbs = []
for i in range(n_irrep):
    virtual_orbs += range(homos[i] + 1, irrep_orb[i + 1] + 1)
# filter out the occupied orbitals in the active space
virtual_orbs = list(filter(lambda orb: orb not in active_orbs, \
                                                  virtual_orbs))
if debug:
    # print the core, active space and virtual orbitals
    print('core_orbs: ' + str(core_orbs))
    print('active_orbs: ' + str(active_orbs))
    print('virtual_orbs: ' + str(virtual_orbs))
    print('')

# test whether all orbitals are adressed exactly once
all_orbs = core_orbs + active_orbs + virtual_orbs
all_orbs.sort()
assert(all_orbs == range(1,irrep_orb[-1] + 1))

# print out the virtual and other orbitals
print('# 1st line = virtual orbitals; 2nd line = ' +
      'other orbitals in sorted order')
print(virtual_orbs)
other_orbs = core_orbs + active_orbs
other_orbs.sort()
print(other_orbs)

# enhance further manipulations
other_orbs = np.array(other_orbs)

permutation = other_orbs - 1  # index == orbital number - 1
if debug:
    # print the permutation
    print('permutation: ' + str(permutation))
    print('')

# do the reordering
orbsym = orbsym[permutation]

new_data = {
    'nelec': nelec,
    'ms2': ms2,
    'uhf': uhf,
    'orbsym': orbsym,
}

# check transfer of data variable
if debug:
    assert((orbsym == new_data['orbsym']).all())

rw.dump_header(header, new_data)
