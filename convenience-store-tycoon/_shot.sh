#!/usr/bin/env bash
# 临时工具（非交付物）：用无头 Edge 把设计稿 HTML 截成 PNG。
set -u
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
SRC="design/mockups"
DST="design/ui-shots"
PROJ="/f/Administrator/Documents/代码/convenience-store-tycoon"
rm -rf /tmp/mockui
mkdir -p /tmp/mockui "$DST"
cp "$SRC"/*.html /tmp/mockui/
cd /tmp/mockui || exit 1
WBASE=$(pwd -W)
for f in *.html; do
  "$EDGE" --headless=new --disable-gpu --hide-scrollbars --no-first-run \
    --window-size=1080,760 --user-data-dir="$WBASE/_prof" \
    "--screenshot=$WBASE/${f%.html}.png" "file:///$WBASE/$f" \
    > /tmp/mockui/edge.log 2>&1
  if [ ! -f "${f%.html}.png" ]; then
    echo "RETRY(legacy headless): $f"
    "$EDGE" --headless --disable-gpu --hide-scrollbars --no-first-run \
      --window-size=1080,760 --user-data-dir="$WBASE/_prof" \
      "--screenshot=$WBASE/${f%.html}.png" "file:///$WBASE/$f" \
      > /tmp/mockui/edge.log 2>&1
  fi
done
echo "--- edge.log tail ---"
tail -3 /tmp/mockui/edge.log
cp /tmp/mockui/*.png "$PROJ/$DST/" 2>/dev/null || true
cd "$PROJ" || exit 1
echo "--- result ---"
ls -la "$DST"
