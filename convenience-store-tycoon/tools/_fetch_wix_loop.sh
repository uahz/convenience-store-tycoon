#!/usr/bin/env bash
# 临时工具（非交付物）：循环断点续传 WiX 包直到完整。
cd "F:/Administrator/Documents/代码/convenience-store-tycoon/tools/wix-local" || exit 1
TARGET=34670186
for i in 1 2 3 4 5 6 7 8 9 10; do
  SIZE=$(stat -c %s wix311-binaries.zip 2>/dev/null || echo 0)
  if [ "$SIZE" = "$TARGET" ]; then
    echo "COMPLETE at $SIZE"
    break
  fi
  echo "attempt $i: have $SIZE / $TARGET"
  curl -L --retry 3 -C - --connect-timeout 30 -sS \
    -o wix311-binaries.zip \
    "https://ghproxy.net/https://github.com/wixtoolset/wix3/releases/download/wix3112rtm/wix311-binaries.zip"
  sleep 2
done
SIZE=$(stat -c %s wix311-binaries.zip 2>/dev/null || echo 0)
echo "final size: $SIZE (target $TARGET)"
