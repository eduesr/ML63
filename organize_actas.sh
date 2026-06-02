#!/bin/bash
BASE="/Users/eduardosr/Documents/GitHub/ML63/Recursos"
SRC="$BASE/varios../actas y cosas"
DEST="$BASE/Actas"

mkdir -p "$DEST/Junta 2015" "$DEST/Junta 2016" "$DEST/Junta 2017" "$DEST/Junta 2018" "$DEST/Junta 2020" "$DEST/Junta 2021" "$DEST/Junta 2022"

cp "$SRC/ModestoLafuente62.ctas2015.pdf" "$DEST/Junta 2015/"
cp "$SRC/Modesto lafuente140316 2016.pdf" "$DEST/Junta 2016/"
cp "$SRC/ModestoLafuente63.ctas2016-17_20180405121944.pdf" "$DEST/Junta 2017/"
cp "$SRC/M. Lafuente acta 24 abril 18_20180508113709.pdf" "$DEST/Junta 2018/"
cp "$SRC/ModestoLafuente63.ctas2018_20190726094857.pdf" "$DEST/Junta 2018/"
cp "$SRC/MODESTOLAFUENTE63.ACTA151020-virtual.pdf" "$DEST/Junta 2020/"
cp "$SRC/MODESTOLAFUENTE63.07-1221.pdf" "$DEST/Junta 2021/" 2>/dev/null || cp "$SRC/ModestoLafuente63.07-1221.pdf" "$DEST/Junta 2021/"
cp "$SRC/ModestoLafuente63.ctas2020-21_20210721101330.pdf" "$DEST/Junta 2021/"
cp "$SRC/ModestoLafuente63.acta280322.pdf" "$DEST/Junta 2022/"
cp "$SRC/ModestoLafuente63.nota-inf150322.pdf" "$DEST/Junta 2022/"

echo "Done organizing actas."
