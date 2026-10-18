#!/usr/bin/env bash
# 当 github.com:443 不通（git push 被阻断）时，改用 api.github.com 建 commit 并强更 ref。
# 做法：把本地 HEAD 的完整 tree 逐文件上传成 blob → 建 tree（不带 base_tree）→ 建 commit（parent=远端 main）→ PATCH ref(force)。
# 这样不依赖本地是否握有远端对象，远端内容永远等于本地 HEAD 的内容。
# 用法: bash push_api.sh ["commit message"]
set -euo pipefail
cd "$(dirname "$0")"
WORK=$(pwd -W)
GH="/c/Program Files/GitHub CLI/gh.exe"
REPO="dapeng3369-jpg/jiaxing-kezhang"
MSG="${1:-$(git log -1 --format=%s)}"

BASE=$("$GH" api "repos/$REPO/git/ref/heads/main" --jq .object.sha)
echo "remote base=$BASE  local HEAD=$(git rev-parse HEAD)"

ENTRIES=""
while IFS=$'\t' read -r meta path; do
  set -- $meta
  mode="$1"; type="$2"; sha="$3"
  [ "$type" = "blob" ] || continue
  B64=$(git cat-file -p "$sha" | base64 -w0)
  printf '{"content":"%s","encoding":"base64"}' "$B64" > "$WORK/.gh_tmp_blob.json"
  NEW=$("$GH" api "repos/$REPO/git/blobs" -X POST --input "$WORK/.gh_tmp_blob.json" --jq .sha)
  ENTRIES="$ENTRIES{\"path\":\"$path\",\"mode\":\"$mode\",\"type\":\"blob\",\"sha\":\"$NEW\"},"
  echo "blob $path -> $NEW"
done < <(git -c core.quotepath=false ls-tree -r HEAD)

ENTRIES="${ENTRIES%,}"
printf '{"tree":[%s]}' "$ENTRIES" > "$WORK/.gh_tmp_tree.json"
TREE=$("$GH" api "repos/$REPO/git/trees" -X POST --input "$WORK/.gh_tmp_tree.json" --jq .sha)
echo "tree=$TREE  (local $(git rev-parse HEAD^{tree}))"

A_NAME=$(git log -1 --format=%an); A_EMAIL=$(git log -1 --format=%ae); A_DATE=$(git log -1 --format=%aI)
C_NAME=$(git log -1 --format=%cn); C_EMAIL=$(git log -1 --format=%ce); C_DATE=$(git log -1 --format=%cI)
printf '{"message":"%s","tree":"%s","parents":["%s"],"author":{"name":"%s","email":"%s","date":"%s"},"committer":{"name":"%s","email":"%s","date":"%s"}}' \
  "$MSG" "$TREE" "$BASE" "$A_NAME" "$A_EMAIL" "$A_DATE" "$C_NAME" "$C_EMAIL" "$C_DATE" > "$WORK/.gh_tmp_commit.json"
NEWC=$("$GH" api "repos/$REPO/git/commits" -X POST --input "$WORK/.gh_tmp_commit.json" --jq .sha)
echo "commit=$NEWC"

printf '{"sha":"%s","force":true}' "$NEWC" > "$WORK/.gh_tmp_ref.json"
"$GH" api "repos/$REPO/git/refs/heads/main" -X PATCH --input "$WORK/.gh_tmp_ref.json" --jq .object.sha
rm -f "$WORK"/.gh_tmp_*.json
echo "pushed via API: $MSG"
