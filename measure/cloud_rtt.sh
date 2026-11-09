#!/bin/sh
# Cloud round-trip from YOUR location to any uncached HTTPS endpoint (default: RAWA's trivial API ping).
# A real POS call (write a sale) costs at least this much, so this is a lower bound for any cloud-only POS.
# usage: ./cloud_rtt.sh [url] [samples]
URL="${1:-https://rawaerp.com/api/method/ping}"; N="${2:-20}"
i=1; while [ $i -le $N ]; do
  curl -s -o /dev/null -w "%{time_total}\n" "$URL?_=$RANDOM$i"; i=$((i+1))
done | python3 -c "
import sys,statistics
v=sorted(float(l)*1000 for l in sys.stdin if l.strip())
print('n=%d  min=%.0f  median=%.0f  p95=%.0f  max=%.0f  (ms)' % (len(v), v[0], statistics.median(v), v[max(0,int(.95*len(v))-1)], v[-1]))"
