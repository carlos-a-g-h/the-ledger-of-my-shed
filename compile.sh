#!/bin/bash

OUTDIR="the-output"
PKGDIR="shled"

# SHLED's main binary
NAME_BIN1="shled"

# SHLED's Message Shipment Daemon
NAME_BIN2="smsd"

python -m nuitka --onefile --follow-imports --assume-yes-for-downloads --remove-output --output-dir="$OUTDIR" --output-filename="$NAME_BIN1" "main.py"
if [ $? -eq 0 ]
then
	ldd "the-output/main.dist/$NAME_BIN1" > "$PKGDIR/$NAME_BIN1.ldd.txt"
else
	echo "FAILED TO COMPILE $NAME_BIN1"
	exit 1
fi

#python -m nuitka --onefile --follow-imports --assume-yes-for-downloads --remove-output --output-dir="$OUTDIR" --output-filename="$NAME_BIN2" "main_broker.py"
#if [ $? -eq 0 ]
#then
#	ldd "the-output/main.dist/$NAME_BIN2" > "$PKGDIR/$NAME_BIN2.ldd.txt"
#else
#	echo "FAILED TO COMPILE $NAME_BIN2"
#	exit 1
#fi

find
