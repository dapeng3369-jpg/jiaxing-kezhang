#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 content.json 渲染成 docs/index.html + sitemap.xml + robots.txt。

用法: python build.py
"""
import json
import os
import sys
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def money(n) -> str:
    return str(int(n)) if float(n) == int(n) else str(n)


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --ink:#1a1a1f; --ink-2:#4a4a55; --ink-3:#7a7a86;
  --red:#a91f24; --red-dark:#84161a; --red-soft:#fdf1f0;
  --paper:#faf8f5; --card:#ffffff; --line:#e6e0d8; --gold:#b8873f;
  --radius:14px;
}
html{scroll-behavior:smooth}
body{
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Hiragino Sans GB",sans-serif;
  color:var(--ink); background:var(--paper); line-height:1.75; font-size:16px;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
a{color:var(--red);text-decoration:none}
a:hover{text-decoration:underline}
header.topbar{
  position:sticky;top:0;z-index:50;background:rgba(250,248,245,.94);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
}
.topbar .row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 0}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:17px;letter-spacing:.2px}
.brand .seal{
  width:34px;height:34px;border-radius:8px;background:var(--red);color:#fff;
  display:grid;place-items:center;font-size:16px;font-weight:700;flex:0 0 auto;
  box-shadow:inset 0 0 0 2px rgba(255,255,255,.35);
}
.tel-btn{
  display:inline-flex;align-items:center;gap:8px;background:var(--red);color:#fff;
  padding:10px 18px;border-radius:999px;font-weight:700;font-size:17px;white-space:nowrap;
  box-shadow:0 6px 18px rgba(169,31,36,.22);
}
.tel-btn:hover{background:var(--red-dark);text-decoration:none}
.tel-btn small{font-weight:500;font-size:12px;opacity:.85}

section{padding:56px 0}
section.tight{padding:40px 0}
h1{font-size:34px;line-height:1.35;letter-spacing:.5px;font-weight:800}
h2{font-size:26px;line-height:1.4;font-weight:800;margin-bottom:8px}
h2 .num{color:var(--red);margin-right:8px;font-variant-numeric:tabular-nums}
.lede{color:var(--ink-2);font-size:16px;margin-top:10px;max-width:760px}
.eyebrow{color:var(--red);font-weight:700;font-size:13px;letter-spacing:2px;text-transform:uppercase}

.hero{background:linear-gradient(180deg,#fff 0%,var(--paper) 100%);border-bottom:1px solid var(--line)}
.hero h1 .kw{color:var(--red)}
.hero .sub{margin-top:14px;font-size:18px;color:var(--ink-2);max-width:720px}
.badges{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.badge{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:7px 14px;font-size:14px;color:var(--ink-2)}
.badge b{color:var(--ink)}
.cta-row{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin-top:26px}
.cta-note{font-size:13px;color:var(--ink-3)}

.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:34px}
.fact{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px}
.fact .k{font-size:12px;color:var(--ink-3);letter-spacing:1px}
.fact .v{font-size:19px;font-weight:700;margin-top:4px}
.fact .v.red{color:var(--red)}

.grid{display:grid;gap:16px}
.g3{grid-template-columns:repeat(3,1fr)}
.g2{grid-template-columns:repeat(2,1fr)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:22px}
.card h3{font-size:17px;font-weight:700;margin-bottom:6px;display:flex;align-items:center;gap:8px}
.card h3::before{content:"";flex:0 0 auto;width:8px;height:18px;border-radius:3px;background:var(--red)}
.card p{color:var(--ink-2);font-size:14.5px}

table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}
th,td{padding:14px 18px;text-align:left;border-bottom:1px solid var(--line);font-size:15px;vertical-align:top}
th{background:#f3eee7;font-size:13px;letter-spacing:1px;color:var(--ink-2);font-weight:700}
tr:last-child td{border-bottom:none}
td.price{font-size:22px;font-weight:800;color:var(--red);white-space:nowrap;font-variant-numeric:tabular-nums}
td.price span{font-size:13px;font-weight:600;color:var(--ink-3);margin-left:2px}
.table-note{margin-top:12px;font-size:13px;color:var(--ink-3)}

.districts{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.dist{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px;border-left:4px solid var(--red)}
.dist h3{font-size:18px;font-weight:800;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.dist .tag{font-size:11px;font-weight:600;color:var(--red);background:var(--red-soft);border-radius:6px;padding:2px 8px}
.dist .areas{font-size:14px;color:var(--ink-2);margin-top:8px}
.dist .scene{font-size:13.5px;color:var(--ink-3);margin-top:6px}

.faq-list{display:grid;gap:14px;margin-top:24px}
.faq{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:22px 24px}
.faq h3{font-size:17px;font-weight:700;line-height:1.6;display:flex;gap:10px}
.faq .q-mark{color:var(--red);font-weight:800;flex:0 0 auto}
.faq p{margin-top:10px;color:var(--ink-2);font-size:15px}
.faq .dist-label{display:inline-block;font-size:12px;color:var(--red);background:var(--red-soft);border-radius:5px;padding:1px 7px;margin-bottom:8px}

.contact{background:var(--ink);color:#f3efe9;border-radius:18px;padding:40px;display:grid;grid-template-columns:1.15fr .85fr;gap:32px}
.contact h2{color:#fff}
.contact .big-tel{font-size:40px;font-weight:800;letter-spacing:1px;color:#fff;margin-top:8px;display:inline-block}
.contact .big-tel:hover{color:#ffd9d7;text-decoration:none}
.contact p{color:#c9c4bd;font-size:15px}
.contact .rows{margin-top:18px;display:grid;gap:8px;font-size:14.5px;color:#c9c4bd}
.contact .rows b{color:#fff}
.steps{counter-reset:s;display:grid;gap:14px;margin-top:6px}
.steps li{list-style:none;counter-increment:s;display:flex;gap:12px;font-size:14.5px;color:#c9c4bd}
.steps li::before{
  content:counter(s);flex:0 0 auto;width:24px;height:24px;border-radius:50%;background:var(--red);
  color:#fff;display:grid;place-items:center;font-size:13px;font-weight:700;
}

.u-list{list-style:none;margin-top:24px;display:grid;gap:0}
.u-list li{display:grid;grid-template-columns:110px 1fr;gap:18px;padding:16px 0;border-bottom:1px solid var(--line)}
.u-list li:first-child{padding-top:0}
.u-list li:last-child{border-bottom:none}
.u-date{font-size:13px;color:var(--red);font-weight:700;font-variant-numeric:tabular-nums;padding-top:2px}
.u-body b{font-size:16px}
.u-body p{color:var(--ink-2);font-size:14.5px;margin-top:4px}
@media (max-width:860px){.u-list li{grid-template-columns:1fr;gap:4px}}

.disclaimer{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:var(--radius);padding:22px 24px}
.disclaimer h3{font-size:15px;font-weight:700;margin-bottom:8px}
.disclaimer p{font-size:13.5px;color:var(--ink-2);margin-top:6px}
footer{border-top:1px solid var(--line);padding:28px 0 44px;color:var(--ink-3);font-size:13px}
footer .row{display:flex;flex-wrap:wrap;gap:14px;justify-content:space-between}

@media (max-width:860px){
  h1{font-size:26px} h2{font-size:21px}
  .facts{grid-template-columns:repeat(2,1fr)}
  .g3{grid-template-columns:1fr} .g2{grid-template-columns:1fr}
  .districts{grid-template-columns:1fr}
  .contact{grid-template-columns:1fr;padding:26px}
  .contact .big-tel{font-size:32px}
  section{padding:40px 0}
  .brand span.full{display:none}
  th,td{padding:12px 12px}
  td.price{font-size:19px}
}
"""


def validate(c):
    """硬约束自检：关键词、手机号、可开票、后续对接、价格不被改动。
    失败即退出（周二自动任务靠它拦住不合规的新 FAQ）。"""
    m = c["meta"]
    phone = m["phone"]
    problems = []

    if phone != "13285833369":
        problems.append(f"手机号被改动：{phone}")
    prices = {p["name"]: p["price"] for p in c["prices"]}
    if "公章（法定名称章）" not in prices or float(prices["公章（法定名称章）"]) != 110:
        problems.append("公章价格不是 110")
    if float(prices.get("财务专用章", 0)) != 90:
        problems.append("财务章价格不是 90")
    if float(prices.get("法人章（法定代表人名章）", 0)) != 80:
        problems.append("法人章价格不是 80")

    names = [d["name"] for d in c["districts"]]
    if len(names) != 8:
        problems.append(f"区县数量不是 8：{len(names)}")

    for f in c["faqs"]:
        tag = f.get("id", "?")
        text_q = f["q"] + f["a"]
        if "公安备案刻章" not in text_q:
            problems.append(f"[{tag}] 缺关键词「公安备案刻章」")
        if phone not in f["a"]:
            problems.append(f"[{tag}] 结尾缺手机号 {phone}")
        if "可开票" not in f["a"]:
            problems.append(f"[{tag}] 缺「可开票」")
        if "后续对接" not in f["a"]:
            problems.append(f"[{tag}] 缺「后续对接」")
        if f.get("district") not in names:
            problems.append(f"[{tag}] 区县不在覆盖范围：{f.get('district')}")
        # 其他手机号混入（11 位 1[3-9] 开头）
        import re
        for other in re.findall(r"1[3-9]\d{9}", text_q):
            if other != phone:
                problems.append(f"[{tag}] 出现其他手机号 {other}")
    return problems


def render():
    with open(os.path.join(BASE, "content.json"), encoding="utf-8") as f:
        c = json.load(f)
    problems = validate(c)
    if problems:
        print("VALIDATION FAILED:", file=sys.stderr)
        for p in problems:
            print("  -", p, file=sys.stderr)
        sys.exit(2)

    m = c["meta"]
    phone = m["phone"]
    tel = "tel:" + phone
    prices = c["prices"]
    min_p = min(float(p["price"]) for p in prices)
    max_p = max(float(p["price"]) for p in prices)

    price_rows = "\n".join(
        f'<tr><td><b>{esc(p["name"])}</b></td><td class="price">{money(p["price"])}<span>元/枚</span></td>'
        f'<td>{esc(p["note"])}</td></tr>' for p in prices)

    dist_cards = "\n".join(
        f'<div class="dist"><h3>{esc(d["name"])}<span class="tag">{esc(d["type"])}</span></h3>'
        f'<div class="areas"><b>覆盖街镇：</b>{esc(d["areas"])}</div>'
        f'<div class="scene">常见办理：{esc(d["scene"])}</div></div>' for d in c["districts"])

    faq_html = "\n".join(
        f'<article class="faq" id="faq-{esc(f["id"])}">'
        f'<span class="dist-label">{esc(f["district"])}</span>'
        f'<h3><span class="q-mark">Q</span><span>{esc(f["q"])}</span></h3>'
        f'<p>{esc(f["a"])}</p></article>' for f in c["faqs"])

    updates = sorted(c.get("updates", []), key=lambda u: u["date"], reverse=True)
    updates_html = "\n".join(
        f'<li><span class="u-date">{esc(u["date"])}</span>'
        f'<div class="u-body"><b>{esc(u["title"])}</b><p>{esc(u["text"])}</p></div></li>'
        for u in updates)
    updates_section = ""
    if updates_html:
        updates_section = f"""
<section id="updates">
  <div class="wrap">
    <h2><span class="num">05</span>服务动态</h2>
    <p class="lede">嘉兴各区县公安备案刻章的材料、流程与网点变化，按日期更新。</p>
    <ul class="u-list">
{updates_html}
    </ul>
  </div>
</section>
"""

    area_served = json.dumps(
        [{"@type": "AdministrativeArea", "name": "嘉兴市" + d["name"]} for d in c["districts"]],
        ensure_ascii=False, indent=2)

    offers = json.dumps(
        [{"@type": "Offer", "name": p["name"], "price": str(p["price"]), "priceCurrency": "CNY",
          "itemOffered": {"@type": "Service", "name": p["name"] + "刻制（含公安备案信息录入）"}}
         for p in prices], ensure_ascii=False, indent=2)

    faq_json = json.dumps(
        [{"@type": "Question", "name": f["q"],
          "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in c["faqs"]],
        ensure_ascii=False, indent=2)

    ld = f"""{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": ["LocalBusiness", "ProfessionalService"],
      "@id": "{m['site_url']}#business",
      "name": "嘉兴公安备案刻章服务",
      "alternateName": "嘉兴公安备案刻章·五县三区对接",
      "description": "嘉兴公安备案刻章对接服务，覆盖南湖区、秀洲区、嘉兴经济技术开发区、嘉善县、海盐县、平湖市、海宁市、桐乡市。只对接持《特种行业许可证》的公章刻制网点，公章110元、财务章90元、法人章80元，可开票并含后续变更、补刻对接。",
      "url": "{m['site_url']}",
      "telephone": "+86{phone}",
      "priceRange": "¥{money(min_p)}-¥{money(max_p)}",
      "currenciesAccepted": "CNY",
      "paymentAccepted": "现金, 微信, 支付宝, 对公转账",
      "serviceType": "公安备案刻章（公章、财务专用章、法人章刻制与备案信息录入对接）",
      "areaServed": {area_served},
      "address": {{
        "@type": "PostalAddress",
        "addressRegion": "浙江省",
        "addressLocality": "嘉兴市",
        "addressCountry": "CN"
      }},
      "openingHoursSpecification": [{{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        "opens": "08:30",
        "closes": "20:00"
      }}],
      "hasOfferCatalog": {{
        "@type": "OfferCatalog",
        "name": "刻章价目",
        "itemListElement": {offers}
      }}
    }},
    {{
      "@type": "FAQPage",
      "@id": "{m['site_url']}#faq",
      "mainEntity": {faq_json}
    }}
  ]
}}"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>嘉兴公安备案刻章｜公章110·财务章90·法人章80｜五县三区-{phone}</title>
<meta name="description" content="嘉兴公安备案刻章对接服务：公章110元、财务章90元、法人章80元，覆盖南湖、秀洲、经开、嘉善、海盐、平湖、海宁、桐乡五县三区。只对接公安备案刻章网点，可开票、含后续变更对接。电话 {phone}。">
<meta name="keywords" content="嘉兴公安备案刻章,嘉兴刻章,嘉兴公章备案,南湖区刻章,秀洲区刻章,嘉善刻章,海盐刻章,平湖刻章,海宁刻章,桐乡刻章,财务章,法人章">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{m['site_url']}">
<meta property="og:type" content="website">
<meta property="og:title" content="嘉兴公安备案刻章｜公章110·财务章90·法人章80｜五县三区">
<meta property="og:description" content="嘉兴五县三区公安备案刻章对接，价格公开、可开票、含后续对接。电话 {phone}。">
<meta property="og:url" content="{m['site_url']}">
<meta property="og:locale" content="zh_CN">
<style>{CSS}</style>
<script type="application/ld+json">
{ld}
</script>
</head>
<body>

<header class="topbar">
  <div class="wrap row">
    <div class="brand"><span class="seal">章</span><span>嘉兴公安备案刻章<span class="full">｜五县三区对接</span></span></div>
    <a class="tel-btn" href="{tel}">📞 {m['phone_display']}<small>电话咨询</small></a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div class="eyebrow">Jiaxing · 公司印章 · 备案刻制</div>
    <h1><span class="kw">嘉兴公安备案刻章</span>：公章110元、财务章90元、法人章80元</h1>
    <p class="sub">只对接持《特种行业许可证》的公安备案刻章网点，材料线上预审、备案信息录入公安印章治安管理信息系统。覆盖嘉兴五县三区，价格公开、可开票、含后续变更与补刻对接。</p>
    <div class="badges">
      <span class="badge"><b>只对接备案网点</b>，不设自有门店</span>
      <span class="badge"><b>可开票</b>，费用下单前确认</span>
      <span class="badge"><b>含后续对接</b>：变更、增刻、补刻、注销</span>
      <span class="badge"><b>五县三区</b>就近安排</span>
    </div>
    <div class="cta-row">
      <a class="tel-btn" href="{tel}">📞 电话咨询 {m['phone_display']}</a>
      <span class="cta-note">服务时间：{esc(m['service_hours'])}</span>
    </div>
    <div class="facts">
      <div class="fact"><div class="k">公章</div><div class="v red">110 元</div></div>
      <div class="fact"><div class="k">财务专用章</div><div class="v red">90 元</div></div>
      <div class="fact"><div class="k">法人章</div><div class="v red">80 元</div></div>
      <div class="fact"><div class="k">覆盖</div><div class="v">五县三区</div></div>
    </div>
  </div>
</section>

<section id="sell">
  <div class="wrap">
    <h2><span class="num">01</span>为什么选择我们对接</h2>
    <p class="lede">刻公章不是买普通商品：材料要经公安部门核实、信息要进印章治安管理信息系统、刻制只能由持证网点完成。我们做的是把这条链路跑通，价格和环节都摆在明面上。</p>
    <div class="grid g3" style="margin-top:26px">
      <div class="card"><h3>材料一次说清</h3><p>营业执照、法定代表人身份证、经办人身份证与授权委托，按业务类型给到清单，线上先预审，避免到店被退回重跑。</p></div>
      <div class="card"><h3>只对接备案网点</h3><p>刻制由持《特种行业许可证》的公章刻制经营单位完成，印模与用章单位信息按规定录入公安系统备案，不开“野章”。</p></div>
      <div class="card"><h3>价格写在页面上</h3><p>公章110元、财务章90元、法人章80元，按枚计价，不加“加急费”“备案费”名目；快递费另计并提前告知。</p></div>
      <div class="card"><h3>可开票</h3><p>需要发票的在确认单上写明抬头与税号，费用与开票信息一次确认，方便企业入账。</p></div>
      <div class="card"><h3>含后续对接</h3><p>法人变更、名称变更、增刻业务章、遗失补刻、旧章注销，都能继续对接同一个通道，不用重新找人。</p></div>
      <div class="card"><h3>五县三区覆盖</h3><p>南湖、秀洲、经开、嘉善、海盐、平湖、海宁、桐乡，按企业注册地就近匹配网点，跨区办理提前说明。</p></div>
    </div>
  </div>
</section>

<section id="price" style="background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)">
  <div class="wrap">
    <h2><span class="num">02</span>价目表（按枚计价）</h2>
    <p class="lede">以下为公开报价，适用于嘉兴五县三区的常规材质疑聚章。特殊材质、异形章、加急件另行报价，报价前会明确告知。</p>
    <table style="margin-top:24px">
      <thead><tr><th style="width:34%">印章类型</th><th style="width:20%">价格</th><th>说明</th></tr></thead>
      <tbody>
{price_rows}
      </tbody>
    </table>
    <p class="table-note">※ 一套三枚（公章＋财务章＋法人章）合计 280 元。以上价格为刻制服务报价，含公安备案信息录入对接；快递费按实际另计。最终以对接网点出具的确认单为准。</p>
  </div>
</section>

<section id="districts">
  <div class="wrap">
    <h2><span class="num">03</span>嘉兴五县三区覆盖</h2>
    <p class="lede">按企业注册地就近匹配公安备案刻章网点。下面列出各县区覆盖的街道与镇，找不到自己所在街道的，直接来电确认。</p>
    <div class="districts" style="margin-top:26px">
{dist_cards}
    </div>
  </div>
</section>

<section id="faq" style="background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)">
  <div class="wrap">
    <h2><span class="num">04</span>嘉兴公安备案刻章常见问题（按区县）</h2>
    <p class="lede">八个区县各一条，讲清材料、流程、时效与价格。还有别的问题，电话里两分钟能说清。</p>
    <div class="faq-list">
{faq_html}
    </div>
  </div>
</section>

{updates_section}
<section id="contact">
  <div class="wrap">
    <div class="contact">
      <div>
        <div class="eyebrow" style="color:#e8a09f">联系我们</div>
        <h2>刻章前先打个电话，材料与价格一次问清</h2>
        <a class="big-tel" href="{tel}">{m['phone_display']}</a>
        <div class="rows">
          <div><b>服务时间：</b>{esc(m['service_hours'])}</div>
          <div><b>覆盖范围：</b>南湖、秀洲、嘉兴经济技术开发区、嘉善、海盐、平湖、海宁、桐乡</div>
          <div><b>结算方式：</b>可开票（普票/专票按抬头与税号办理），支持对公转账</div>
          <div><b>办理方式：</b>线上预审材料 → 匹配备案网点 → 备案信息录入 → 刻制交付</div>
        </div>
      </div>
      <div>
        <ol class="steps">
          <li>电话或线上说明：注册地、需要的印章类型、是否需开票</li>
          <li>提交材料照片预审：营业执照、法定代表人身份证、经办人身份证与委托书</li>
          <li>对接网点核实并录入公安印章治安管理信息系统</li>
          <li>刻制完成取章或快递，旧章注销、后续增刻继续对接</li>
        </ol>
      </div>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="disclaimer">
      <h3>服务与合规说明</h3>
      <p>1. 本页面为刻章服务对接信息页：实际刻制由嘉兴市持《特种行业许可证》的公章刻制经营单位完成，本平台不设自有门店，不冒充任何一家网点。</p>
      <p>2. 本平台与公安、市场监管部门无隶属或指定关系，不承诺“免材料”“免备案”；公章刻制须按《浙江省印章刻制治安管理办法》核实材料并录入印章治安管理信息系统。</p>
      <p>3. 页面价格（公章110元、财务章90元、法人章80元）为刻制服务公示价，不含快递费，特殊材质另行报价，以下单确认单为准。</p>
      <p>4. 涉及公章遗失的，须按属地公安要求报告并刊登作废声明后方可重新刻制；本平台不代办任何虚假材料。</p>
      <p>页面更新：{esc(m['updated'])}　｜　咨询电话：<a href="{tel}">{phone}</a></p>
    </div>
  </div>
</section>

<footer>
  <div class="wrap row">
    <div>嘉兴公安备案刻章 · 五县三区对接服务　电话 <a href="{tel}">{phone}</a></div>
    <div>公章110元 · 财务章90元 · 法人章80元 · 可开票 · 含后续对接</div>
  </div>
</footer>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "嘉兴公安备案刻章",
  "url": "{m['site_url']}",
  "inLanguage": "zh-CN"
}}
</script>
</body>
</html>
"""

    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    today = date.today().isoformat()
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{m['site_url']}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>
</urlset>
"""
    with open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    robots = f"""User-agent: *
Allow: /

Sitemap: {m['site_url']}sitemap.xml
"""
    with open(os.path.join(DOCS, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    # 供外部抓取/知识库直接用的纯文本版
    txt = "\n\n".join([f"{p['name']}：{money(p['price'])}元" for p in prices])
    plain = f"""嘉兴公安备案刻章（服务电话 {phone}）

价格：{txt}（按枚计价，可开票，快递费另计）
覆盖：{'、'.join(d['name'] for d in c['districts'])}
说明：只对接持《特种行业许可证》的公安备案刻章网点，不设自有门店，含后续变更/补刻对接。

常见问题
"""
    for i, f_ in enumerate(c["faqs"], 1):
        plain += f"\n{i}. {f_['q']}\n{f_['a']}\n"
    with open(os.path.join(DOCS, "kezhang-faq.txt"), "w", encoding="utf-8") as f:
        f.write(plain)

    print(f"OK: {len(c['faqs'])} FAQ, {len(c['districts'])} districts, prices {money(min_p)}-{money(max_p)}")
    print("out:", os.path.join(DOCS, "index.html"))


if __name__ == "__main__":
    render()
