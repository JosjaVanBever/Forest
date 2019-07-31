'''
python3 script to construct a tensor network file for T3NS
'''


from collections import deque
import sys
import random
import os
import os.path as path
import shutil

# check the arguments
if len(sys.argv) != 3:  # incl. python script
    error_message = 'Syntaxis: python plant.py FCIDUMP ' + \
                  'SEED'
    raise IOError(error_message)
# try interpreting the arguments as files
fcidump = sys.argv[1]
seed = sys.argv[2]
# test wether these files can be opened
test = open(sys.argv[1])
test.close()
test = open(sys.argv[2])
test.close()


# make temporary files to store the several output pieces
tmp_dir = 'tmpplant' + str(random.randint(0,999999))
os.mkdir(tmp_dir)
# print('tmp_dir was: %s' % tmp_dir)
header = path.join(tmp_dir, 'header')
tree = path.join(tmp_dir, 'tree')


# dictionaries to keep track of the labels
groups = {}
branchtensors = {}
# read in the orbital numbers from the fcidump file
with open(fcidump) as f:
    # parse the orbsym array
    line = next(f).lstrip()
    while not line.startswith('ORBSYM'):
        line = next(f).lstrip()
    key, value = line.split('=')
    orbsym = list(value.strip(',\n').split(','))
    # create a group dictionary from it
    for i in list(set(orbsym)):
        groups[i] = deque([])
    for i in range(len(orbsym)):
        groups[orbsym[i]].append(i)

# the groups dictionary can be visually verified
# print(groups)


# help function:
# get the right orbital number for a certain label
branchtensornr = len(orbsym)
def nr(label):
    global groups, branchtensors, branchtensornr
    if label in groups:
        result = groups[label].popleft()
    elif label in branchtensors:
        result = branchtensors[label]
    else:
        result = branchtensornr
        branchtensors[label] = branchtensornr
        branchtensornr += 1
    return result

# create a temporary file for the actual tree
tmp_file = 'tmp' + str(random.randint(0,999999))
# print('tmp_file was: %s' % tmp_dir)

# loop over the seed and construct the tree
nr_bonds = 0
with open(tree, "w") as t:
    with open(seed) as f:
        for line in f:
            words = line.split()
            nbrs = []
            # give all orbitals a unique label
            if words[0] in groups:
                nbrs.append(-1)
            for tensor in words:
                nbrs.append(nr(tensor))
            # write out the given branch
            for i in range(1, len(nbrs)):
                nr_bonds += 1
                t.write(str(nbrs[i-1]) + ' ' + str(nbrs[i]) + '\n')
            last = nbrs[-1]
    nr_bonds += 1
    t.write(str(last) + ' -1')

nr_phys_sites = len(orbsym)
nr_sites = nr_phys_sites + len(branchtensors)

with open(header, 'w') as f:
    # write out the header
    f.write('NR_SITES = %d\n' % nr_sites)
    f.write('NR_PHYS_SITES = %d\n' % nr_phys_sites)
    f.write('NR_BONDS = %d\n' % nr_bonds)
    f.write('/\n')
    convertion = [i for i in range(len(orbsym))] + \
            ['*' for i in range(nr_sites - nr_phys_sites)]
    for orb in range(len(convertion)):
        f.write(str(convertion[orb]) + ' ')
    #f.write(str(*convertion) + '\n')
    f.write('\n/END\n')

# bash way:
#  os.system("cat " + header + " " + tree)
# pythonic way:
print(''.join([open(f).read() for f in [header, tree]]))
# remove the temporary directory
shutil.rmtree(tmp_dir)
