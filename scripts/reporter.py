#!/usr/bin/env python3
"""
Benchmark Radar - HTML 报告生成器
输入: radar.py 产出的 candidates JSON (从 stdin 或 --input 文件)
输出: HTML 报告 (--output 路径)

用法:
    python -X utf8 radar.py "做付费咨询" | python -X utf8 reporter.py --output report.html
    python -X utf8 reporter.py --input candidates.json --output report.html
"""

import argparse
import datetime
import html
import json
import sys
from pathlib import Path


HTML_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Benchmark Radar · 对标雷达报告</title>
<style>
  :root {
    --ink: #1a1a1a;
    --paper: #ffffff;
    --paper-soft: #f7f6f2;
    --line: #e5e3dc;
    --accent: #1d4f3f;
    --accent-soft: #e8f0ec;
    --warn: #b91c1c;
    --muted: #6b6b6b;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    background: var(--paper);
    color: var(--ink);
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 920px; margin: 0 auto; padding: 48px 32px 80px; }
  .brand {
    display: flex; align-items: baseline; gap: 12px;
    border-bottom: 2px solid var(--ink);
    padding-bottom: 16px;
  }
  .brand h1 { font-size: 28px; margin: 0; letter-spacing: -0.5px; }
  .brand .tag {
    font-size: 12px; color: var(--muted); letter-spacing: 1px; text-transform: uppercase;
  }
  .meta { display: flex; flex-wrap: wrap; gap: 24px; margin-top: 16px; font-size: 13px; color: var(--muted); }
  .meta span strong { color: var(--ink); font-weight: 500; }

  .summary {
    background: var(--accent-soft);
    border-left: 4px solid var(--accent);
    padding: 20px 24px;
    margin: 32px 0 16px;
    font-size: 15px;
  }
  .summary h2 { margin: 0 0 8px; font-size: 14px; color: var(--accent); letter-spacing: 1px; text-transform: uppercase; }
  .summary p { margin: 6px 0; }

  .reject {
    background: #fef2f2;
    border-left: 4px solid var(--warn);
    padding: 20px 24px;
    margin: 32px 0;
    color: var(--warn);
  }
  .reject h2 { margin: 0 0 8px; font-size: 16px; }

  .card {
    background: var(--paper-soft);
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 28px 28px 24px;
    margin: 20px 0;
  }
  .card-head {
    display: flex; align-items: flex-start; justify-content: space-between; gap: 16px;
    border-bottom: 1px dashed var(--line); padding-bottom: 14px; margin-bottom: 16px;
  }
  .card-head .name { font-size: 20px; font-weight: 600; margin: 0 0 4px; }
  .card-head .cat { font-size: 12px; color: var(--muted); }
  .clone-total {
    background: var(--ink); color: var(--paper);
    padding: 6px 14px; border-radius: 999px;
    font-size: 13px; font-weight: 500;
    white-space: nowrap;
  }

  .clone-bars { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin: 12px 0 20px; }
  .clone-cell {
    background: var(--paper);
    border: 1px solid var(--line);
    padding: 10px 8px;
    text-align: center;
    border-radius: 3px;
  }
  .clone-cell .letter {
    display: block;
    font-size: 18px; font-weight: 700; color: var(--accent);
    font-family: "SF Mono", Consolas, monospace;
  }
  .clone-cell .label { display: block; font-size: 10px; color: var(--muted); letter-spacing: 0.5px; text-transform: uppercase; margin: 2px 0; }
  .clone-cell .score { font-size: 14px; font-weight: 600; }
  .clone-cell.weak .score { color: var(--warn); }

  .r-grid { margin: 16px 0; border: 1px solid var(--line); border-radius: 3px; overflow: hidden; }
  .r-row { display: grid; grid-template-columns: 80px 1fr; border-bottom: 1px solid var(--line); }
  .r-row:last-child { border-bottom: none; }
  .r-key { background: var(--paper); padding: 12px 14px; font-weight: 600; font-size: 13px; color: var(--accent); border-right: 1px solid var(--line); }
  .r-key small { display: block; font-weight: 400; color: var(--muted); font-size: 10px; letter-spacing: 0.5px; text-transform: uppercase; }
  .r-val { padding: 12px 14px; font-size: 14px; }
  .r-val ul { margin: 0; padding-left: 20px; }
  .r-val li { margin: 2px 0; }

  .actions { margin-top: 18px; }
  .actions h4 { font-size: 13px; color: var(--accent); letter-spacing: 1px; text-transform: uppercase; margin: 0 0 10px; }
  .timeline { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
  .step {
    background: var(--paper); border: 1px solid var(--line); padding: 12px 14px; border-radius: 3px;
    font-size: 13px;
  }
  .step .when { font-size: 11px; font-weight: 700; color: var(--accent); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }

  .links { margin-top: 16px; font-size: 13px; }
  .links h4 { font-size: 13px; color: var(--accent); letter-spacing: 1px; text-transform: uppercase; margin: 0 0 8px; }
  .links a { color: var(--accent); word-break: break-all; }
  .links li { margin: 3px 0; }

  .one-liner {
    margin-top: 16px; padding-top: 14px; border-top: 1px dashed var(--line);
    font-style: italic; color: var(--ink); font-size: 14px;
  }

  .bottom {
    margin-top: 48px; padding-top: 32px; border-top: 2px solid var(--ink);
  }
  .bottom h2 { font-size: 18px; margin: 0 0 16px; }
  .bottom .qs { background: var(--paper-soft); padding: 20px 24px; border-left: 4px solid var(--accent); }
  .bottom .qs ol { margin: 0; padding-left: 20px; }
  .bottom .qs li { margin: 8px 0; font-size: 14px; }

  .verdict {
    margin-top: 24px; padding: 24px;
    background: var(--ink); color: var(--paper);
    font-size: 16px; line-height: 1.6;
    border-radius: 4px;
  }
  .verdict::before { content: "「"; color: var(--accent); font-size: 24px; }
  .verdict::after { content: "」"; color: var(--accent); font-size: 24px; }

  .footer {
    margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--line);
    font-size: 11px; color: var(--muted); letter-spacing: 0.5px;
  }
</style>
</head>
<body>
<div class="wrap">
"""

HTML_TAIL = """
  <div class="footer">
    Benchmark Radar · 对标雷达 — 由 CLONE 五道闸门 + 5R 复刻矩阵驱动 ·
    方法论受 dontbesilent 启发，工程实现独立。
  </div>
</div>
</body>
</html>
"""


def esc(s) -> str:
    if s is None:
        return ""
    return html.escape(str(s))


def render_clone_bars(clone: dict) -> str:
    keys = [
        ("C", "Cash 真赚钱", "cash"),
        ("L", "Logic 逻辑透明", "logic"),
        ("O", "Operability 可仿", "operability"),
        ("N", "No Self 排除我", "no_self"),
        ("E", "Evidence 证据链", "evidence"),
    ]
    cells = []
    for letter, label, key in keys:
        score = clone.get(key, 0)
        weak_class = " weak" if score < 6 else ""
        cells.append(
            f'<div class="clone-cell{weak_class}">'
            f'<span class="letter">{letter}</span>'
            f'<span class="label">{esc(label)}</span>'
            f'<span class="score">{score}/10</span>'
            f'</div>'
        )
    return f'<div class="clone-bars">{"".join(cells)}</div>'


def render_5r(case: dict) -> str:
    rows = []

    rate = case.get("rate", {})
    rate_html = "<ul>"
    if rate.get("main_price"):
        rate_html += f"<li>主产品定价：{esc(rate['main_price'])}</li>"
    if rate.get("price_ladder"):
        rate_html += f"<li>价差结构：{esc(rate['price_ladder'])}</li>"
    if rate.get("hook_vs_profit"):
        rate_html += f"<li>引流款 vs 利润款：{esc(rate['hook_vs_profit'])}</li>"
    rate_html += "</ul>"
    rows.append(("R1", "Rate 价格", rate_html))

    reach = case.get("reach", {})
    reach_html = "<ul>"
    if reach.get("platform"):
        reach_html += f"<li>主获客平台：{esc(reach['platform'])}</li>"
    if reach.get("content_form"):
        reach_html += f"<li>内容形式：{esc(reach['content_form'])}</li>"
    if reach.get("frequency"):
        reach_html += f"<li>发布频率：{esc(reach['frequency'])}</li>"
    reach_html += "</ul>"
    rows.append(("R2", "Reach 触达", reach_html))

    rhetoric = case.get("rhetoric", {})
    rhet_html = "<ul>"
    if rhetoric.get("title_template"):
        rhet_html += f"<li>标题模板：{esc(rhetoric['title_template'])}</li>"
    if rhetoric.get("cover_elements"):
        rhet_html += f"<li>封面元素：{esc(rhetoric['cover_elements'])}</li>"
    if rhetoric.get("tone"):
        rhet_html += f"<li>文案调性：{esc(rhetoric['tone'])}</li>"
    rhet_html += "</ul>"
    rows.append(("R3", "Rhetoric 话语", rhet_html))

    routine = case.get("routine", {})
    rt_html = "<ul>"
    if routine.get("delivery"):
        rt_html += f"<li>交付流程：{esc(routine['delivery'])}</li>"
    if routine.get("promotion"):
        rt_html += f"<li>促销手段：{esc(routine['promotion'])}</li>"
    if routine.get("repurchase"):
        rt_html += f"<li>复购触发：{esc(routine['repurchase'])}</li>"
    rt_html += "</ul>"
    rows.append(("R4", "Routine 闭环", rt_html))

    reality = case.get("reality", {})
    real_html = ""
    if reality.get("snapshot"):
        real_html += f"<div>数据快照：{esc(reality['snapshot'])}</div>"
    if reality.get("links"):
        real_html += '<ul style="margin-top:8px">'
        for link in reality["links"]:
            real_html += f'<li><a href="{esc(link.get("url",""))}" target="_blank" rel="noopener">{esc(link.get("label","链接"))}</a></li>'
        real_html += "</ul>"
    rows.append(("R5", "Reality 现场", real_html))

    parts = []
    for k, label, body in rows:
        parts.append(
            f'<div class="r-row">'
            f'<div class="r-key">{k}<small>{esc(label)}</small></div>'
            f'<div class="r-val">{body}</div>'
            f'</div>'
        )
    return f'<div class="r-grid">{"".join(parts)}</div>'


def render_actions(actions: dict) -> str:
    items = [
        ("today", "今天", actions.get("today", "—")),
        ("week", "本周", actions.get("week", "—")),
        ("month", "本月", actions.get("month", "—")),
    ]
    cells = "".join(
        f'<div class="step"><div class="when">{esc(label)}</div>{esc(body)}</div>'
        for _, label, body in items
    )
    return f'<div class="actions"><h4>三段行动起点</h4><div class="timeline">{cells}</div></div>'


def render_card(case: dict, idx: int) -> str:
    clone = case.get("clone", {})
    clone_total = sum(clone.get(k, 0) for k in ("cash", "logic", "operability", "no_self", "evidence"))

    name = case.get("name", "未命名对标")
    category = case.get("category", "")
    business = case.get("business", "")
    profit_low = case.get("monthly_profit_wan_low", "?")
    profit_high = case.get("monthly_profit_wan_high", "?")

    head = (
        f'<div class="card-head">'
        f'<div>'
        f'<div class="name">#{idx} · {esc(name)}</div>'
        f'<div class="cat">{esc(category)} · {esc(business)} · 估算月利润 ¥{esc(profit_low)}–{esc(profit_high)} 万</div>'
        f'</div>'
        f'<div class="clone-total">CLONE 总分 {clone_total}/50</div>'
        f'</div>'
    )

    parts = [head]
    parts.append(render_clone_bars(clone))
    parts.append(render_5r(case))
    parts.append(render_actions(case.get("actions", {})))

    one_liner = case.get("one_liner")
    if one_liner:
        parts.append(f'<div class="one-liner">{esc(one_liner)}</div>')

    return f'<div class="card">{"".join(parts)}</div>'


def render_report(data: dict) -> str:
    if data.get("status") == "rejected":
        body = (
            f'<div class="brand"><h1>对标雷达</h1><span class="tag">Benchmark Radar</span></div>'
            f'<div class="reject">'
            f'<h2>输入被拒绝 · 落入「自我陷阱」</h2>'
            f'<pre style="white-space:pre-wrap;font-family:inherit;margin:0">{esc(data.get("message", ""))}</pre>'
            f'</div>'
        )
        return HTML_HEAD + body + HTML_TAIL

    query = data.get("query", "")
    candidates = data.get("candidates", [])
    pf = data.get("platform_filter")
    pt = data.get("profit_target_wan")
    fallback = data.get("fallback")
    fb_reason = data.get("fallback_reason")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    head = (
        f'<div class="brand">'
        f'<h1>对标雷达报告</h1>'
        f'<span class="tag">Benchmark Radar · CLONE + 5R</span>'
        f'</div>'
        f'<div class="meta">'
        f'<span>查询：<strong>{esc(query)}</strong></span>'
        f'<span>平台过滤：<strong>{esc(pf or "全平台")}</strong></span>'
        f'<span>利润目标：<strong>{esc(str(pt) + " 万/月" if pt else "未指定")}</strong></span>'
        f'<span>候选数：<strong>{len(candidates)}</strong></span>'
        f'<span>生成时间：<strong>{esc(now)}</strong></span>'
        f'</div>'
    )

    hint = data.get("hint")
    hint_html = ""
    if hint:
        hint_html = (
            f'<div class="summary" style="background:#fef9e7;border-left-color:#d97706">'
            f'<h2 style="color:#92400e">提示</h2>'
            f'<p>{esc(hint)}</p>'
            f'</div>'
        )

    if fallback:
        summary = (
            f'<div class="summary">'
            f'<h2>市场扫描总结（降级模式）</h2>'
            f'<p>{esc(fb_reason or "未在案例库匹配到强相关对标，已按 CLONE 总分降序展示库内通过过滤的全部候选。")}</p>'
            f'<p>建议：换一个更具体的业务方向描述，或拓宽利润目标范围。</p>'
            f'</div>'
        ) + hint_html
    else:
        platforms = sorted({c.get("reach", {}).get("platform", "未知") for c in candidates})
        avg_profit_low = sum(c.get("monthly_profit_wan_low", 0) for c in candidates) / max(len(candidates), 1)
        summary = (
            f'<div class="summary">'
            f'<h2>市场扫描总结</h2>'
            f'<p>· 共有 <strong>{len(candidates)}</strong> 个对标通过 CLONE 五道闸门，按总分降序排列。</p>'
            f'<p>· 主要分布在 <strong>{esc("、".join(platforms))}</strong>。</p>'
            f'<p>· 这批对标的月利润下限平均 <strong>¥{avg_profit_low:.1f} 万</strong>，是市场上"已经被验证"的赚钱方向。</p>'
            f'</div>'
        ) + hint_html

    cards = "".join(render_card(c, i + 1) for i, c in enumerate(candidates))

    bottom = (
        f'<div class="bottom">'
        f'<h2>你必须自己回答的 3 个决策问题</h2>'
        f'<div class="qs">'
        f'<ol>'
        f'<li>这批对标里，哪一个的获客平台是你愿意每天花 1 小时去深耕的？（如果没有，先解决「平台选择」再谈对标）</li>'
        f'<li>这批对标的最低定价是 ¥{candidates[0].get("rate",{}).get("main_price","--") if candidates else "--"}，你愿意先按这个价格收第一笔钱吗？（如果不愿意，先解决「定价心理障碍」）</li>'
        f'<li>这批对标的"今天能做的事"里，你今晚 22 点之前会真的做哪一件？（如果一个都不会做，对标就只是收藏夹素材）</li>'
        f'</ol>'
        f'</div>'
        f'<div class="verdict">市场不缺对标，缺的是把"今天能做的事"真的做了的人。这份报告 24 小时内不开始第一步动作的话，AI 给你再多对标都是噪音。</div>'
        f'</div>'
    )

    return HTML_HEAD + head + summary + cards + bottom + HTML_TAIL


def main():
    parser = argparse.ArgumentParser(description="Benchmark Radar HTML 报告生成器")
    parser.add_argument("--input", default=None, help="candidates JSON 文件路径（默认从 stdin 读）")
    parser.add_argument("--output", required=True, help="HTML 输出路径")
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    html_content = render_report(data)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] 报告已生成: {out_path}")


if __name__ == "__main__":
    main()
