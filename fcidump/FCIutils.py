# -*- coding: utf-8 -*-
# HORTON: Helpful Open-source Research TOol for N-fermion systems.
# Copyright (C) 2011-2017 The HORTON Development Team
#
# This file is part of HORTON.
#
# HORTON is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# HORTON is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --

import sys
__all__ = ['set_four_index_element']


def set_four_index_element(four_index_object, i, j, k, l, value):
    """Assign values to a four index object, account for 8-fold index symmetry.
    This function assumes physicists' notation
    Parameters
    ----------
    four_index_object : np.ndarray, shape=(nbasis, nbasis, nbasis, nbasis), dtype=float
        The four-index object
    i, j, k, l: int
        The indices to assign to.
    value : float
        The value of the matrix element to store.
    """
    four_index_object[i, j, k, l] = value
    four_index_object[j, i, l, k] = value
    four_index_object[k, j, i, l] = value
    four_index_object[i, l, k, j] = value
    four_index_object[k, l, i, j] = value
    four_index_object[l, k, j, i] = value
    four_index_object[j, k, l, i] = value
    four_index_object[l, i, j, k] = value

def print_two_mo(i,j,k,l):
    print('(%d,%d,%d,%d) = two_mo[%d-1,%d-1,%d-1,%d-1] = %.20e' % (i,j,k,l,i,k,j,l,two_mo[i-1,k-1,j-1,l-1]))

# dictionary that contains the mapping from molpro irrep convention
# to psi4 irrep convention, starting from 0: psi = mol2psi[mol]
mol2psi = {}
for key in ['C1']:
    mol2psi[key] = [0]
for key in ['Ci', 'C2', 'Cs']:
    mol2psi[key] = [0, 1]
for key in ['D2']:
    mol2psi[key] = [0, 3, 2, 1]
for key in ['C2v', 'C2h']:
    mol2psi[key] = [0, 2, 3, 1]
for key in ['D2h']:
    mol2psi[key] = [0, 7, 6, 1, 5, 2, 3, 4]
# dictionary that contains the mapping from PSI4 irrep convention
# to molpro irrep convention, starting from 0: mol = psi2mol[psi]
psi2mol = {}
for key in ['C1']:
    psi2mol[key] = [0]
for key in ['Ci', 'C2', 'Cs']:
    psi2mol[key] = [0, 1]
for key in ['D2']:
    psi2mol[key] = [0, 3, 2, 1]
for key in ['C2v', 'C2h']:
    psi2mol[key] = [0, 3, 1, 2]
for key in ['D2h']:
    psi2mol[key] = [0, 3, 5, 6, 7, 4, 2, 1]


# ##### write to pkl #####
# dump = open("fcidump.pkl", "wb")
# pickle.dump(data, dump, -1)
# dump.close()
#
# ##### load from pkl #####
# dump = open("fcidump.pkl", "rb")
# data = pickle.load(dump)


# ##### save data to a binary #####
# np.save('orbsym', orbsym)
# np.save('one_mo', one_mo)
# np.save('two_mo', two_mo)
# np.save('core_energy', core_energy)
# np.save('nelec', nelec)
#
# ##### load data from a binary #####
# orbsym = np.load('orbsym.npy')
# one_mo = np.load('one_mo.npy')
# two_mo = np.load('two_mo.npy')
# core_energy = np.load('core_energy.npy')
# nelec = np.load('nelec.npy')
