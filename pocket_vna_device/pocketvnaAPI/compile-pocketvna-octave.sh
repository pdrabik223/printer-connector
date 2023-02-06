#!/usr/bin/bash
mkoctfile  -v -Wl,/home/mntmnt/Projects/projectadc/device-api/libPocketVnaApi_x64.so  pocketvna_octave.cc
if [ $? -ne 0 ]; then
	echo "-----FAILED TO mkoctfile"
	exit 1
fi
patchelf --set-rpath '$ORIGIN/./' pocketvna_octave.oct
if [ $? -ne 0 ]; then
	echo "-----FAILED to patch rpath"
	exit 1
fi

