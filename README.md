# 嘉兴公安备案刻章 — 静态站构建与发布

内容在 `content.json`，模板在 `build.py`，产物生成到 `docs/`（GitHub Pages 从这里发布）。

## 改内容
只改 `content.json`：价格 `prices`、区县 `districts`、FAQ `faqs`。不要手改 `docs/`（会被覆盖）。

## 构建（含硬校验）
```
python build.py
```
`build.py` 会先跑 `validate()`，不通过直接退出码 2，不生成页面。校验项：
- 手机号必须是 13285833369，且 FAQ 里不出现别的手机号
- 价格必须是 公章110 / 财务章90 / 法人章80
- 区县必须是 8 个
- 每条 FAQ 必须含「公安备案刻章」「可开票」「后续对接」和手机号

## 发布
```
bash deploy.sh "说明文字"
```
脚本自动选代理（本机代理没开时直连 github.com），build → commit → push → 触发 Pages 重建。

线上地址：https://dapeng3369-jpg.github.io/jiaxing-kezhang/

## 每周二自动追加 FAQ
```
python add_faq.py --file new_faq.json
```
`new_faq.json` 形如 {"district":"海宁市","q":"...","a":"..."}。
`add_faq.py` 校验 → 追加 content.json → 构建 → 发布 → 写 faq-log.md。
