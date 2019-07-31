#!/bin/bash

# @param
# $1 : the FCIDUMP file to manipulate
# $2 : the orborder file

# @error
# exit 1 : syntax error
# exit 2 : no valid python module

date

# syntax print for error messages
SYNTAX="Syntaxis: FCImanip INFILE OUTFILE ORBORDER"

if [ $# != '3' ]
then
  echo "${SYNTAX}" 1>&2
  exit 1
fi

FCIDUMP="$1"
OUTFILE="$2"
ORBORDER="$3"
TMP="tmp$$"

mkdir "${TMP}"
cd "${TMP}"

# split the FCIDUMP file
split -10000 "../${FCIDUMP}" FCI #5000000 
part1='FCIaa'
HEADLENGTH=$(( $(grep -n -m1 '&END' "${part1}" | cut -d':' -f1) + 1 ))
csplit -f FCI_ "${part1}" "${HEADLENGTH}" > /dev/null
# FCI_00 now contains the header and FCI* are the integrals
mv FCI_00 header
mv FCI_01 FCIaa

python "${CRFBIN}"/fcidump/FCIfilter.py header "../${ORBORDER}" |
  sed 's/,//g; s/\[//g; s/\]//g' > filter

# # split the file in header and integrals
# HEADLENGTH=$(( $(grep -n -m1 '&END' ${FCIDUMP} | cut -d':' -f1) + 1 ))
# csplit -f FCI "${FCIDUMP}" "${HEADLENGTH}" > /dev/null
# # FCI00 now contains the header and FCI01
# # contains the integrals

# echo ${TODO} | xargs -n1 --max-procs "${THREADS}" bash -c '
# echo "${PARENTID}/$$: start optimising $1.com"; g16 "${1}".com
# echo "${PARENTID}/$$: Geometry is optimised with ${1}.com!"' bash

# split -5000000 FCI01 int_

exec 3< 'filter'
# skip the header
read line 0<&3
# read the virtual orbitals
read virtual 0<&3
todelete=$(sed 's/ /|/g; s/^/(/; s/$/)/' <<< "${virtual}")
# read the other orbitals
read others 0<&3
replace=''
count='1'
for orb in $others; do
  replace+="s/ ${orb}(\b)/ ${count}\1/g; "
  (( count++ ))
done
echo "$replace"
# for part in FCI*; do
#   sed -i -E "/ ${todelete}( |$)/d; ${replace}" "${part}"
#   # sed -i -E "/[eE].*[^0-9]${todelete}[^0-9]/d" "${part}"
#   # sed -i -E "${replace}" "${part}"
# done

export todelete
export replace

echo FCI* | xargs -n1 --max-procs 6 bash -c '
echo "handling $1"
sed -i -E "/ ${todelete}\b/d" "$1"
sed -i -E "${replace}" "$1"' bash


# for orb in $virtual; do
#   for part in FCI*; do
#     sed -i "/[eE].*[^0-9]${orb}[^0-9]/d" "${part}"
#   done
# done

alphabetic=$(find . -name "FCI??" -print0 | sort -z | xargs -0 echo)
cat header ${alphabetic} > novirtual.FCIDUMP

python "${CRFBIN}"/fcidump/FCImanip.py novirtual.FCIDUMP ../"${OUTFILE}" ../"${ORBORDER}"

date

cd ..
# rm -r "${TMP}"

exit 0
