#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加一条 FAQ 到站点：校验 → 写 content.json → 构建 → 发布 → 记日志。

用法:
  python add_faq.py --file new_faq.json
  python add_faq.py --json '{"district":"海宁市","q":"...","a":"..."}'

必填字段: district（必须是八个区县之一）、q、a
约束由 build.validate() 双向把关，这里先做一遍更早的拦截。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(BASE, "content.json")
LOG = os.path.join(BASE, "faq-log.md")


def load():
    with open(CONTENT, encoding="utf-8") as f:
        return json.load(f)


def check(c, item):
    errs = []
    phone = c["meta"]["phone"]
    names = [d["name"] for d in c["districts"]]
    d = item.get("district", "")
    q = item.get("q", "").strip()
    a = item.get("a", "").strip()

    if d not in names:
        errs.append(f"district 必须是以下之一：{'、'.join(names)}")
    if len(q) < 8:
        errs.append("问题太短")
    if not (60 <= len(a) <= 420):
        errs.append(f"答案长度 {len(a)}，要求 60–420 字")
    joined = q + a
    if "公安备案刻章" not in joined:
        errs.append("缺关键词「公安备案刻章」")
    if not a.rstrip("。 ").endswith(phone):
        errs.append(f"答案必须以手机号 {phone} 结尾")
    if "可开票" not in a:
        errs.append("缺「可开票」")
    if "后续对接" not in a:
        errs.append("缺「后续对接」")
    for other in re.findall(r"1[3-9]\d{9}", joined):
        if other != phone:
            errs.append(f"出现其他手机号 {other}（只允许 {phone}）")
    # 与现有问题重复
    for f in c["faqs"]:
        if f["q"].strip() == q:
            errs.append("与已有 FAQ 问题完全相同")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--json")
    ap.add_argument("--no-deploy", action="store_true", help="只构建不推送")
    a = ap.parse_args()
    if a.file:
        item = json.load(open(a.file, encoding="utf-8"))
    elif a.json:
        item = json.loads(a.json)
    else:
        sys.exit("需要 --file 或 --json")

    c = load()
    errs = check(c, item)
    if errs:
        print("拒绝写入：", file=sys.stderr)
        for e in errs:
            print("  -", e, file=sys.stderr)
        sys.exit(3)

    stamp = datetime.now().strftime("%Y%m%d")
    item["id"] = f"{stamp}-{len(c['faqs']) + 1}"
    c["faqs"].append({
        "id": item["id"],
        "district": item["district"],
        "q": item["q"].strip(),
        "a": item["a"].strip(),
    })
    c["meta"]["updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(CONTENT, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)

    print(f"已追加 FAQ id={item['id']} district={item['district']} 总数={len(c['faqs'])}")

    r = subprocess.run([sys.executable, os.path.join(BASE, "build.py")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(r.returncode)

    deploy_ok, deploy_out = False, ""
    if not a.no_deploy:
        r2 = subprocess.run(["bash", os.path.join(BASE, "deploy.sh"), f"FAQ 更新 {item['id']}"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        deploy_ok = r2.returncode == 0
        deploy_out = (r2.stdout + r2.stderr).strip().splitlines()[-3:]
        print("\n".join(deploy_out))

    line = (f"- {datetime.now().strftime('%Y-%m-%d %H:%M')} | {item['district']} | {item['q']} "
            f"| id={item['id']} | 构建通过 | 发布{'成功' if deploy_ok else '未完成'} | FAQ 总数 {len(c['faqs'])}\n")
    newfile = not os.path.exists(LOG)
    with open(LOG, "a", encoding="utf-8") as f:
        if newfile:
            f.write("# 嘉兴备案刻章 FAQ 追加日志\n\n")
        f.write(line)

    print("log:", LOG)
    sys.exit(0 if deploy_ok or a.no_deploy else 4)


if __name__ == "__main__":
    main()
