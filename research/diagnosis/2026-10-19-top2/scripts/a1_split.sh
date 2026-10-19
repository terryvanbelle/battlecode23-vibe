#!/usr/bin/env bash
# a1_split.sh SA_DIR OUT_DIR RMAX: split each <match><side>/sa_{L,C,HQ}.csv (--sa --games all) by game, rounds < RMAX,
# into OUT_DIR/<match>g<game><side>/sa_X.csv (header kept). Column 2 = game, column 4 = round.
set -euo pipefail
SA=$1; OUT=$2; RMAX=$3
for d in "$SA"/*; do
  b=$(basename "$d")
  for f in sa_L sa_C sa_HQ; do
    [ -f "$d/$f.csv" ] || continue
    awk -F, -v out="$OUT" -v b="$b" -v f="$f" -v rmax="$RMAX" '
      NR==1 { hdr=$0; next }
      $4 < rmax { m=substr(b,1,length(b)-1); s=substr(b,length(b),1); dir=out "/" m "g" $2 s; p=dir "/" f ".csv";
                  if (!(p in seen)) { system("mkdir -p " dir); print hdr > p; seen[p]=1 } print >> p }' "$d/$f.csv"
  done
done
