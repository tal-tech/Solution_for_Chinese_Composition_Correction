#!/bin/bash

program=$1
dumpname=$2

./dump_syms $program > $program.sym
uuid=`head -n1 $program.sym | awk '{print $4}'`
prodir=`head -n1 $program.sym | awk '{print $5}'`
mkdir -p symbols/$prodir/$uuid
mv $program.sym symbols/$prodir/$uuid
./minidump_stackwalk $dumpname symbols/ > $dumpname.txt

