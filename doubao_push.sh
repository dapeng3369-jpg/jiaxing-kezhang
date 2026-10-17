#!/usr/bin/env bash
# 把一段文本作为消息推送到豆包指定对话，用于追加知识库内容。
# 用法: bash doubao_push.sh <消息文件> [对话URL]
# 依赖: 本地 Chrome 以 --remote-debugging-port=9222 启动且已登录豆包
set -uo pipefail
MSG="${1:?需要消息文件}"
CHAT_URL="${2:-https://www.doubao.com/chat/38447647393542146}"
SCRATCH="$LOCALAPPDATA/hermes/cache/scratch"
CDP="$SCRATCH/cdp.mjs"
PROFILE="C:/Users/mengd/AppData/Local/hermes/browser-profiles/doubao"

cdp_ready() {
  curl -s -m 3 http://127.0.0.1:9222/json/version >/dev/null 2>&1
}

if ! cdp_ready; then
  echo "CDP 未就绪，启动专用 Chrome…"
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
    --remote-debugging-port=9222 --user-data-dir="$PROFILE" \
    --no-first-run --no-default-browser-check --window-size=1440,960 \
    "$CHAT_URL" >/dev/null 2>&1 &
  for i in $(seq 1 20); do
    cdp_ready && break
    sleep 1
  done
  cdp_ready || { echo "FAIL: Chrome 起不来或 9222 端口不可用"; exit 2; }
fi

node "$CDP" nav "$CHAT_URL" || { echo "FAIL: 导航失败（可能未登录豆包）"; exit 3; }
sleep 4
node "$CDP" shot "$SCRATCH/_push_before.png" >/dev/null 2>&1 || true

# 检查登录态
LOGIN=$(node "$CDP" eval "(()=>{const t=document.body.innerText; return /登录|扫码/.test(t.slice(0,260)) ? 'no' : 'yes'})()")
if [ "$LOGIN" != "yes" ]; then
  echo "FAIL: 豆包未登录，需要人工扫码"
  exit 4
fi

node "$CDP" eval "(()=>{const el=document.querySelector('textarea,[contenteditable=true]'); if(!el) return 'no'; el.focus(); return 'ok'})()" | grep -q ok || {
  echo "FAIL: 找不到输入框"; exit 5; }
node "$CDP" type --file "$MSG" >/dev/null
sleep 1
node "$CDP" key Enter >/dev/null
echo "已发送，等待豆包处理…"

OK=""
for i in $(seq 1 40); do
  sleep 6
  TAIL=$(node "$CDP" eval "document.body.innerText.replace(/\s+/g,' ').slice(-500)")
  case "$TAIL" in
    *"已写入"*|*"已更新"*|*"知识库文件已"*|*"写入"*)
      OK="yes"; echo "豆包已处理: ${TAIL: -200}"; break ;;
  esac
  echo "$TAIL" | grep -q "正在思考\|正在准备\|正在运行\|正在阅读" || {
    # 既没有思考态，也没命中关键词：再等一轮
    :
  }
done

node "$CDP" shot "$SCRATCH/_push_after.png" >/dev/null 2>&1 || true
if [ -z "$OK" ]; then
  echo "WARN: 未检测到明确的写入确认，请查看 $SCRATCH/_push_after.png"
  exit 6
fi
echo "OK: 知识库推送完成"
