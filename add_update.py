#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加一条服务动态（每日更新用）：校验 → 写 content.json → 构建 → 发布 → 记日志。

用法:
  python add_update.py --json '{"title":"...","text":"..."}' [--date 2026-10-18]
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(BASE, "content.json")
LOG = os.path.join(BASE, "update-log.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--date")
    ap.add_argument("--no-deploy", action="store_true")
    a = ap.parse_args()
    item = json.loads(a.json)
    title = item.get("title", "").strip()
    text = item.get("text", "").strip()
    date = a.date or datetime.now().strftime("%Y-%m-%d")

    errs = []
    if not (4 <= len(title) <= 40):
        errs.append("标题需 4–40 字")
    if not (40 <= len(text) <= 260):
        errs.append(f"正文需 40–260 字，当前 {len(text)}")
    if any(x in text for x in ("第一", "最好", "唯一指定", "官方指定")):
        errs.append("含极限词或误导性表述")
    if errs:
        print("拒绝写入：", file=sys.stderr)
        for e in errs:
            print("  -", e, file=sys.stderr)
        sys.exit(3)

    c = json.load(open(CONTENT, encoding="utf-8"))
    ups = c.setdefault("updates", [])
    if any(u["title"] == title for u in ups):
        print("拒绝写入：标题重复", file=sys.stderr)
        sys.exit(3)
    ups.append({"date": date, "title": title, "text": text})
    c["meta"]["updated"] = datetime.now().strftime("%Y-%m-%d")
    json.dump(c, open(CONTENT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    r = subprocess.run([sys.executable, os.path.join(BASE, "build.py")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(r.returncode)

    ok = True
    if not a.no_deploy:
        r2 = subprocess.run(["bash", os.path.join(BASE, "deploy.sh"), f"动态 {date} {title}"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        ok = r2.returncode == 0
        print((r2.stdout + r2.stderr).strip()[-300:])

    newf = not os.path.exists(LOG)
    with open(LOG, "a", encoding="utf-8") as f:
        if newf:
            f.write("# 服务动态日志\n\n")
        f.write(f"- {datetime.now().strftime('%Y-%m-%d %H:%M')} | {date} | {title} | "
                f"发布{'成功' if ok else '失败'} | 动态总数 {len(ups)}\n")
    sys.exit(0 if ok else 4)


if __name__ == "__main__":
    main()
