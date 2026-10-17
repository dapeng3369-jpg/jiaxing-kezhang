#!/usr/bin/env bash
# 构建并发布到 GitHub Pages。用法: bash deploy.sh "本次改动说明"
set -euo pipefail
cd "$(dirname "$0")"
MSG="${1:-update site}"

python build.py

# 自动选代理：本机代理未开启时直连 github.com（已实测直连可用）
PX=""
for p in 7897 7890 10808 10809; do
  if timeout 2 bash -c "</dev/tcp/127.0.0.1/$p" >/dev/null 2>&1; then
    case "$p" in
      7897|10809) PX="socks5h://127.0.0.1:$p" ;;
      *)          PX="http://127.0.0.1:$p" ;;
    esac
    break
  fi
done

GIT="git -c http.https://github.com.proxy=${PX} -c https.https://github.com.proxy=${PX}"
$GIT add -A
if $GIT diff --cached --quiet; then
  echo "no changes to publish"
  exit 0
fi
$GIT -c user.name="Hermes Bot" -c user.email="bot@local" commit -m "$MSG"
$GIT push origin main
echo "pushed: $MSG"
