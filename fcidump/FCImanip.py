# -*- coding: utf-8 -*-
# Program to manipulate the orbital choice and ordering read from
# an FCIDUMP file. The result is written out to a new FCIDUMP file.

import FCIutils as ut
import fcidumpRW as rw
import pickle
import numpy as np
import random
import sys


# check the arguments
if len(sys.argv) != 4:  # incl. python script
    error_message = 'Syntaxis: python FCImanip.py INPUTFILE ' + \
                  'OUTPUTFILE ORBORDERFILE'
    raise IOError(error_message)
# try interpreting the argumetns as files
oldfcidump = sys.argv[1]
newfcidump = sys.argv[2]
orborderfile = sys.argv[3]
# test wether these files can be opened
test = open(sys.argv[1])
test.close()
test = open(sys.argv[2], 'w')
test.close()
test = open(sys.argv[3])
test.close()

# switch to DEBUGGING MODE
# REMARK: the debugging mode is NOT tested for trivial core,
# active or virtual space
# REMARK: functions calcE and monitor simplify further debugging
debug = False

##### load the FCIDUMP #####
data = rw.load_fcidump(oldfcidump)


##### collect data from FCIDUMP #####
# the irrepnbrs of the active orbitals
orbsym = data['orbsym']
# the one and two electron integrals
one_mo = data['one_mo']
two_mo = data['two_mo']
# the core energy en the number of electrons
core_energy = data['core_energy']
nelec = data['nelec']
# total spin of the system and type of HF
ms2 = data['ms2']
uhf = data['uhf']


# extra for comparison
if debug:
    sum_one_old = np.einsum('ij->', one_mo)
    sum_two_old = np.einsum('ijkl->', two_mo)
    sum_old = sum_one_old + sum_two_old + core_energy
    print('Core_energy_old: ' + str(core_energy))
    print('Sum_one_mo_old: ' + str(sum_one_old))
    print('Sum_two_mo_old: ' + str(sum_two_old))
    print('Total_sum_old ' + str(sum_old))
    print('')
    core_energy_old = core_energy


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

# print intermediate results
print('irrep_orb: ' + str(irrep_orb))
print('occupations: ' + str(occupations))
print('occupied_inds: ' + str(occupied_inds))
print('homos: ' + str(homos))
print('')

# calculate the total energy
def calcE():
    print('Core: %.16f' % core_energy)
    # remark: factor 2 due to sum over the spins
    one_mo_E = 2 * sum([one_mo[i,i] for i in occupied_inds])
    print('One_mo: %.16f' % one_mo_E)   # tested with scf output!
    # remark: different contributions for different spin combinations
    two_mo_E = 2 * sum([two_mo[i,j,i,j] for i in occupied_inds for j in occupied_inds]) \
        - sum([two_mo[i,j,j,i] for i in occupied_inds for j in occupied_inds])
    print('Two_mo: %.16f' % two_mo_E)   # tested with scf output!
    result = core_energy + one_mo_E + two_mo_E
    return result

# monitor energies
initialE = calcE()
print('Initial energy: %.16f' % initialE)
print('')


# select the occupied orbitals
core_orbs = []
for i in range(n_irrep):
    core_orbs += range(irrep_orb[i] + 1, homos[i] + 1)
# determine the amount of electrons in the active space
nelec = 2 * len([orb for orb in active_orbs if orb in core_orbs])
# filter out the occupied orbitals in the active space
if debug:
    print('core_orbs before filtering: ' + str(core_orbs))
core_orbs = list(filter(lambda orb: orb not in active_orbs, core_orbs))

# select the virtual orbitals
virtual_orbs = []
for i in range(n_irrep):
    virtual_orbs += range(homos[i] + 1, irrep_orb[i + 1] + 1)
# filter out the occupied orbitals in the active space
virtual_orbs = list(filter(lambda orb: orb not in active_orbs, \
                                                  virtual_orbs))

# print the core, active space and virtual orbitals
print('core_orbs: ' + str(core_orbs))
print('active_orbs: ' + str(active_orbs))
print('virtual_orbs: ' + str(virtual_orbs))
print('')

# test whether all orbitals are adressed exactly once
all_orbs = core_orbs + active_orbs + virtual_orbs
all_orbs.sort()
assert(all_orbs == range(1,irrep_orb[-1] + 1))

# enhance further manipulations
core_orbs = np.array(core_orbs)
active_orbs = np.array(active_orbs)
virtual_orbs = np.array(virtual_orbs)


# prepare the filtering test
if debug:
    if len(core_orbs) > 0 :
        cor = core_orbs[random.randint(0,len(core_orbs) - 1)] - 1
    else :
        cor = -1
    act = active_orbs[random.randint(0,len(active_orbs) - 1)] - 1
    act2 = active_orbs[random.randint(0,len(active_orbs) - 1)] - 1
    act3 = active_orbs[random.randint(0,len(active_orbs) - 1)] - 1
    act4 = active_orbs[random.randint(0,len(active_orbs) - 1)] - 1
    if len(virtual_orbs) > 0 :
        vir = virtual_orbs[random.randint(0,len(virtual_orbs) - 1)] - 1
    else :
        vir = -1
    # print the test orbitals
    print('test: cor = ' + str(cor) + ', act = ' + str(act) + 
          ', act2 = ' + str(act2) + ', vir = ' + str(vir))
    # print elements that shouldn't be set to 0
    print("elements that shouldn't be set to 0: ")
    not_necessary_zero_one_mo = float(one_mo[act, act2])
    print('from one_mo: ' + str(not_necessary_zero_one_mo))
    not_necessary_zero_two_mo = float(two_mo[act, act2, act3, act4])
    print('from two_mo: ' + str(not_necessary_zero_two_mo))
    # monitor the core_energy for testing
    print('core_energy: ' + str(core_energy))
    print('')

# help function for testing
def monitor(i,j,k=-1,l=-1):
    if debug:
        if l == -1:
            print('passed one_mo(%d,%d) = %.16f' % (i, j, one_mo[i,j]))
        else:
            print('passed two_mo(%d,%d,%d,%d) = %.16f' % (i, j, k, l, \
                                                    two_mo[i,j,k,l]))
def monitorE():
    if debug:
        currentE = calcE()
        print('Current energy: %.16f' % currentE)
        print('')


##### filter the 1 electron integrals (one_mo) #####
# REMARK that index == orbital number - 1
# a one_mo is 0 if one of the orbitals is virtual
for orb in virtual_orbs:
    index = orb - 1
    one_mo[index, :] = one_mo[:, index] = 0
# a one_mo is constant if both orbitals are the same core orbital
# and 0 if both orbitals are different core orbitals
for orb in core_orbs:
    index = orb - 1
    monitor(index,index)
    core_energy += 2 * one_mo[index, index]
    one_mo[index, :] = one_mo[:, index] = 0
    monitorE()

# moniter energies
currentE = calcE()
print('Energy after filtering one_mo\'s: %.16f' % currentE)
print('')

# test the filtering of the one_mo
if debug:
    for t1 in [vir, cor, act]:
        for t2 in [vir, cor]:
            assert(one_mo[t1, t2] == 0)
    assert(not_necessary_zero_one_mo == one_mo[act, act2])


##### filter the 2 electron integrals (two_mo) #####
# REMARK that index == orbital number - 1
# a two_mo is 0 if one of the orbitals is virtual
for orb in virtual_orbs:
    index = orb - 1
    two_mo[index, :, :, :] = two_mo[:, index, :, :] = \
    two_mo[:, :, index, :] = two_mo[:, :, :, index] = 0
# a two_mo that contains at 2 or 4 core orbitals can be simplified:
# - two_mo's containing 4 core orbitals reduce to constants
# - two_mo's containing 2 core orbitals and 2 active orbitals
#   reduce to one_mo's
# REMARK that each core annihilatior should be compensated by
# a corresponding creator
for c1 in core_orbs:
    inc1 = c1 - 1
    # the following can be simplified using the symmetry rules !
    monitor(inc1, inc1, inc1, inc1)
    for c2 in core_orbs:   # works for test example
        inc2 = c2 - 1
        core_energy += 2 * two_mo[inc1, inc2, inc1, inc2]
        core_energy -= two_mo[inc1, inc2, inc2, inc1]
    for a1 in active_orbs:
        for a2 in active_orbs:
            ina1 = a1 - 1
            ina2 = a2 - 1
            one_mo[ina1, ina2] += two_mo[inc1, ina1, inc1, ina2]
            one_mo[ina1, ina2] += two_mo[ina1, inc1, ina2, inc1]
            one_mo[ina1, ina2] -= 0.5 * two_mo[inc1, ina1, ina2, inc1]
            one_mo[ina1, ina2] -= 0.5 * two_mo[ina1, inc1, inc1, ina2]

# Since all elements that contain a core orbital yield either 0, a
# constant or one_mo contribution, thes are discarted from the two_mo.
for orb in core_orbs:
    index = orb - 1
    # two_mo[index, :, index, :] = 0
    two_mo[index, :, :, :] = two_mo[:, index, :, :] = \
    two_mo[:, :, index, :] = two_mo[:, :, :, index] = 0

currentE = calcE()
print('Energy after filtering two_mo\'s: %.16f' % currentE)
print('')


# if debug:
#     # test the filtering of the two_mo
#     for t1 in [vir, cor, act]:
#         for t2 in [vir, cor, act]:
#             for t3 in [vir, cor, act]:
#                 for t4 in [vir, cor]:
#                     assert(two_mo[t1,t2,t3,t4] == 0)
#     assert(not_necessary_zero_two_mo == two_mo[act, act2, act3, act4])

# if debug:
#     # prepare testing of the reordering
#     one_mo_old = np.copy(one_mo)
#     two_mo_old = np.copy(two_mo)

# get the permutation
permutation = active_orbs - 1  # index == orbital number - 1
if debug:
    # print the permutation
    print('permutation: ' + str(permutation))
    print('')

# do the reordering
orbsym = orbsym[permutation]
one_mo = one_mo[permutation, :][:, permutation]
# fastest way:
# two_mo = two_mo[permutation, :, :, :][:, permutation, :, :]\
#                    [:, :, permutation, :][:, :, :, permutation]
# memory preserving way:
two_mo = two_mo[permutation, :, :, :]
two_mo = two_mo[:, permutation, :, :]
two_mo = two_mo[:, :, permutation, :]
two_mo = two_mo[:, :, :, permutation]


if debug:
    # extra for comparison
    sum_one_new = np.einsum('ij->', one_mo)
    sum_two_new = np.einsum('ijkl->', two_mo)
    sum_new = sum_one_new + sum_two_new + core_energy
    print('Core_energy_new: ' + str(core_energy))
    print('Sum_one_mo_new: ' + str(sum_one_new))
    print('Sum_two_mo_new: ' + str(sum_two_new))
    print('Total_sum_new ' + str(sum_new))
    print('')
    print('Difference new VS old:')
    print('Core_energy_diff: ' + str(core_energy - core_energy_old))
    print('Sum_one_mo_diff: ' + str(sum_one_new - sum_one_old))
    print('Sum_two_mo_diff: ' + str(sum_two_new - sum_two_old))
    print('Total_sum_diff ' + str(sum_new - sum_old))
    print('')


# if debug:
#     # test the reordering
#     # of the one_mo
#     for i in range(len(active_orbs)):
#         for j in range(len(active_orbs)):
#             assert(one_mo[i,j] == one_mo_old[active_orbs[i]-1, \
#                                              active_orbs[j]-1])
#     # of the two_mo
#     for i in range(len(active_orbs)):
#         for j in range(len(active_orbs)):
#             for k in range(len(active_orbs)):
#                 for l in range(len(active_orbs)):
#                     assert(two_mo[i,j,k,l] == \
#                            two_mo_old[active_orbs[i]-1, active_orbs[j]-1, \
#                                       active_orbs[k]-1, active_orbs[l]-1])

print('conversion completed')
print('write out the resulting FCIDUMP file')

new_data = {
    'nelec': nelec,
    'ms2': ms2,
    'uhf': uhf,
    'orbsym': orbsym,
    'one_mo': one_mo,
    'two_mo': two_mo,
    'core_energy': core_energy,
}

# check transfer of data variable
if debug:
    assert((orbsym == new_data['orbsym']).all())

# write out the result to the new FCIDUMP file
rw.dump_fcidump(newfcidump, new_data)
