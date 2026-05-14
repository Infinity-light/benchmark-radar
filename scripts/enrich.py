#!/usr/bin/env python3
"""
Benchmark Radar - 实时大数据采集器
真实联网调用 3 个公开 JSON API 抓取对标候选：

  1. loot-drop.io 创业坟场      - 真实失败案例 + AI 复盘
     端点: https://www.loot-drop.io/api/database-explore
     无需 token, 1700+ 死亡创业, 包含完整失败叙述

  2. GitHub Search API          - 开源工具变现专题
     端点: https://api.github.com/search/repositories
     无需 token, 限频 10 req/min anonymous

  3. Hacker News Algolia        - Show HN / 独立产品发布专题
     端点: https://hn.algolia.com/api/v1/search
     完全免费, 无限频

用法:
    python -X utf8 enrich.py "vertical farming"
    python -X utf8 enrich.py "AI coding tool" --limit 5 --sources lootdrop,github
    python -X utf8 enrich.py "newsletter" --sources hn

设计:
- 三源并行, 单源失败不阻断
- loot-drop 作为反面教材 (failed_case=true), GitHub/HN 作为正向案例
- 完全离线友好: 网络不通时 stderr 报错 + 返回空数组
- 仅依赖 Python 3.10+ 标准库, 无外部 pip 依赖
"""

import argparse
import json
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


USER_AGENT = "benchmark-radar/0.2 (https://github.com/Infinity-light/benchmark-radar)"
DEFAULT_TIMEOUT = 8


def http_json(url: str, timeout: float = DEFAULT_TIMEOUT) -> dict | list:
    """通用 JSON HTTP GET, 失败抛异常。"""
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---------------- Source 1: loot-drop.io 创业坟场 ----------------

def fetch_lootdrop(query: str, limit: int = 5, timeout: float = DEFAULT_TIMEOUT) -> list[dict]:
    """
    loot-drop.io 创业坟场 - 真实失败案例数据库 (1700+ dead startups)
    API: https://www.loot-drop.io/api/database-explore
    参数: page, pageSize, sort=newest, q=keyword, sector, productType, country, cause
    """
    params = urllib.parse.urlencode({
        "page": 1,
        "pageSize": limit,
        "sort": "newest",
        "q": query,
    })
    url = f"https://www.loot-drop.io/api/database-explore?{params}"
    data = http_json(url, timeout=timeout)
    rows = data.get("rows", []) if isinstance(data, dict) else []

    candidates = []
    for r in rows[:limit]:
        funding = r.get("total_funding") or 0
        funding_m = funding / 1_000_000
        funding_wan = funding / 10_000  # 美元换算成万元（粗略，1$ ≈ 7￥, 但保守不换）

        name = r.get("name", "Unknown")
        sector = r.get("sector", "Unknown")
        product_type = r.get("product_type", "")
        cause = r.get("primary_cause_of_death", "Unknown")
        end_year = r.get("end_year", "Unknown")
        country = r.get("country", "Unknown")
        full_cause = (r.get("cause_of_death") or "")[:300]

        market_potential = r.get("market_potential", 5)
        scalability = r.get("scalability", 5)
        difficulty = r.get("difficulty", 5)

        candidates.append({
            "name": f"☠️ {name} · 已死",
            "category": "失败案例 / 反面教材",
            "business": f"{product_type or sector} | 死于 {end_year} | 死因: {cause}",
            "tags": ["failed_startup", "lootdrop", sector.lower(), product_type.lower() if product_type else "", cause.lower()],
            "platforms": ["lootdrop"],
            "monthly_profit_wan_low": 0,
            "monthly_profit_wan_high": 0,
            "failed_case": True,
            "funding_burned_usd_m": round(funding_m, 1),
            "clone": {
                # 失败案例不适用 CLONE 正向评分, 这里给"反面价值"评分
                # cash: 烧钱量 × 给 0 (失败), 但提供"避坑价值"
                "cash": 0,
                "logic": 8,    # 死因清晰可学
                "operability": 10,  # 反面教材最容易理解
                "no_self": 10,
                "evidence": 9,  # loot-drop 提供完整复盘
            },
            "rate": {
                "main_price": f"💸 烧光 ${funding_m:.1f}M (约 ¥{funding_wan/1000:.0f}k 万)",
                "price_ladder": "失败前的定价历史需另查",
                "hook_vs_profit": "N/A (公司已死)"
            },
            "reach": {
                "platform": "loot-drop.io 创业坟场",
                "content_form": "失败复盘 + AI 写的死因分析",
                "frequency": f"{end_year} 年关闭"
            },
            "rhetoric": {
                "title_template": "Don't be like [name]: [cause]",
                "cover_elements": "💀 案例研究式封面",
                "tone": "复盘、教训式、避坑指南"
            },
            "routine": {
                "delivery": "N/A - 公司不再运营",
                "promotion": "N/A",
                "repurchase": "N/A"
            },
            "reality": {
                "snapshot": f"行业: {sector} | 国家: {country} | 烧钱: ${funding_m:.1f}M | 市场潜力评分: {market_potential}/10 | 可扩展性: {scalability}/10 | 难度: {difficulty}/10",
                "links": [
                    {"label": "loot-drop 详情", "url": f"https://www.loot-drop.io/#{r.get('id', '')}"},
                    {"label": "loot-drop 数据库", "url": "https://www.loot-drop.io/database-view"},
                    {"label": "Google 搜公司新闻", "url": f"https://www.google.com/search?q={urllib.parse.quote(name + ' shutdown')}"},
                ]
            },
            "actions": {
                "today": f"读完 {name} 死因的 300 字摘要: \"{full_cause[:150]}...\"",
                "week": f"找 3 个同行业 ({sector}) 还活着的公司, 看他们怎么解决 {cause} 这个核心问题",
                "month": f"如果你想做 {sector} 方向, 把 {name} 的死因清单做成你的 anti-checklist"
            },
            "one_liner": f"💀 {name} 烧了 ${funding_m:.1f}M 死于「{cause}」—— 这是你不该走的路。",
            "death_summary": full_cause,
            "_source": "lootdrop",
            "_fetched_at": datetime.now().isoformat(timespec="seconds"),
        })
    return candidates


# ---------------- Source 2: GitHub Search Repositories ----------------

def fetch_github(query: str, limit: int = 5, timeout: float = DEFAULT_TIMEOUT) -> list[dict]:
    """
    GitHub Search Repositories API - 仅限"开源工具变现"专题
    无 token, 限频 10/min anonymous, 配合 stars:>50 过滤掉死项目
    """
    q = urllib.parse.quote(f"{query} in:description,readme stars:>50")
    url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={limit}"
    data = http_json(url, timeout=timeout)
    items = data.get("items", []) if isinstance(data, dict) else []

    candidates = []
    for r in items[:limit]:
        stars = r.get("stargazers_count", 0)
        profit_low = round(stars / 1000 * 0.3, 1)
        profit_high = round(stars / 1000 * 1.5, 1)

        candidates.append({
            "name": f"⭐ {r.get('name', '?')} · GitHub",
            "category": "开源项目变现",
            "business": (r.get("description") or "(no description)")[:150],
            "tags": (r.get("topics") or [])[:6] + ["github", "open_source"],
            "platforms": ["github"],
            "monthly_profit_wan_low": profit_low,
            "monthly_profit_wan_high": profit_high,
            "failed_case": False,
            "clone": {
                "cash": min(int(stars / 500), 10),
                "logic": 6,
                "operability": 7,
                "no_self": 10,
                "evidence": 9,
            },
            "rate": {
                "main_price": "免费开源 + GitHub Sponsors / 商业 license",
                "price_ladder": "免费 → Sponsors $5/月 → 商业版 $100-1000/月",
                "hook_vs_profit": "免费开源 → 商业 license 价差需具体看项目"
            },
            "reach": {
                "platform": "GitHub",
                "content_form": "代码 + README + Issues + 社区",
                "frequency": f"最近更新: {(r.get('updated_at') or 'N/A')[:10]}"
            },
            "rhetoric": {
                "title_template": r.get("name", "?"),
                "cover_elements": "README badge + logo + GIF 演示",
                "tone": "技术、开源精神、社区驱动"
            },
            "routine": {
                "delivery": "git clone / pip install / npm install",
                "promotion": "ProductHunt + HN + Twitter + star 病毒传播",
                "repurchase": "持续更新 + 商业版升级 + 培训咨询"
            },
            "reality": {
                "snapshot": f"⭐ {stars} stars · {r.get('forks_count', 0)} forks · {r.get('open_issues_count', 0)} issues · 主语言 {r.get('language', 'N/A')}",
                "links": [
                    {"label": "GitHub 仓库", "url": r.get("html_url", "")},
                    {"label": "作者主页", "url": r.get("owner", {}).get("html_url", "")},
                    {"label": "Issues", "url": r.get("html_url", "") + "/issues"},
                ]
            },
            "actions": {
                "today": f"clone {r.get('full_name', '?')} 读 README, 理解它解决什么问题",
                "week": "在你的领域选一个类似痛点, 做最小开源原型上 GitHub",
                "month": "上 ProductHunt + 写 Show HN, 看是否能复刻流量"
            },
            "one_liner": f"GitHub {stars}⭐ 说明这个方向已被验证有真实用户。",
            "_source": "github",
            "_fetched_at": datetime.now().isoformat(timespec="seconds"),
        })
    return candidates


# ---------------- Source 3: Hacker News Algolia ----------------

def fetch_hn(query: str, limit: int = 5, timeout: float = DEFAULT_TIMEOUT) -> list[dict]:
    """
    HN Algolia Search - 仅限 Show HN / 独立产品发布
    完全免费, 无 auth
    """
    q = urllib.parse.quote(f"Show HN {query}")
    url = f"https://hn.algolia.com/api/v1/search?query={q}&tags=story&hitsPerPage={limit}"
    data = http_json(url, timeout=timeout)
    hits = data.get("hits", []) if isinstance(data, dict) else []

    candidates = []
    for h in hits[:limit]:
        points = h.get("points") or 0
        num_comments = h.get("num_comments") or 0
        profit_low = round(points / 100 * 0.5, 1) if points else 0.5
        profit_high = round(points / 100 * 3, 1) if points else 5
        story_url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"

        candidates.append({
            "name": f"💬 {(h.get('title') or 'Untitled')[:55]} · HN",
            "category": "独立产品 / Show HN",
            "business": (h.get("title") or "")[:150],
            "tags": ["hacker_news", "indie", "show_hn"] + ([h.get("author")] if h.get("author") else []),
            "platforms": ["hacker_news", "indie_hackers"],
            "monthly_profit_wan_low": profit_low,
            "monthly_profit_wan_high": profit_high,
            "failed_case": False,
            "clone": {
                "cash": min(int(points / 200), 10),
                "logic": 5,
                "operability": 7,
                "no_self": 10,
                "evidence": 9,
            },
            "rate": {
                "main_price": "见产品官网 (独立 SaaS 常见 $9-99/月)",
                "price_ladder": "免费试用 → 订阅 → 企业版",
                "hook_vs_profit": "免费 trial → 企业版价差通常 10-100 倍"
            },
            "reach": {
                "platform": "Hacker News + Twitter + ProductHunt",
                "content_form": "Show HN 发帖 + Twitter 实时分享",
                "frequency": f"发布于 {(h.get('created_at') or 'N/A')[:10]}"
            },
            "rhetoric": {
                "title_template": "Show HN: [产品名] – [一句话价值]",
                "cover_elements": "极简 landing page + GIF demo",
                "tone": "简洁、技术直白、anti-bloat"
            },
            "routine": {
                "delivery": "网站注册即用 / 代码下载",
                "promotion": "HN front page + Twitter + ProductHunt 三件套",
                "repurchase": "订阅自动续费 / 升级"
            },
            "reality": {
                "snapshot": f"👍 {points} points · 💬 {num_comments} comments · author: {h.get('author', 'unknown')}",
                "links": [
                    {"label": "HN 讨论", "url": f"https://news.ycombinator.com/item?id={h.get('objectID')}"},
                    {"label": "产品链接", "url": story_url},
                    {"label": "作者 HN", "url": f"https://news.ycombinator.com/user?id={h.get('author', '')}"},
                ]
            },
            "actions": {
                "today": f"读 HN 讨论 https://news.ycombinator.com/item?id={h.get('objectID')} 看 top 评论挖掘真实反馈",
                "week": "访问该产品官网, 列出他的定价 / 落地页结构 / 推广方式",
                "month": "做一个类似定位的最小原型 Show HN, 看市场反应"
            },
            "one_liner": f"HN {points}👍 说明这个方向有真实开发者关注。",
            "_source": "hn",
            "_fetched_at": datetime.now().isoformat(timespec="seconds"),
        })
    return candidates


# ---------------- 主流程 ----------------

SOURCE_FUNCTIONS = {
    "lootdrop": fetch_lootdrop,
    "github": fetch_github,
    "hn": fetch_hn,
}

DEFAULT_SOURCES = "lootdrop,github,hn"


def main():
    parser = argparse.ArgumentParser(description="Benchmark Radar 实时大数据采集")
    parser.add_argument("query", help="搜索关键词 (英文效果最佳, 中文亦可)")
    parser.add_argument("--limit", type=int, default=5, help="每个源最多返回多少个 (默认 5)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"单源超时秒数 (默认 {DEFAULT_TIMEOUT})")
    parser.add_argument("--sources", default=DEFAULT_SOURCES,
                        help=f"启用的源, 逗号分隔 (可选: lootdrop,github,hn). 默认全部启用")
    args = parser.parse_args()

    sources = [s.strip() for s in args.sources.split(",") if s.strip() in SOURCE_FUNCTIONS]
    if not sources:
        print(json.dumps({"status": "error", "reason": "no_valid_sources", "candidates": []}, ensure_ascii=False))
        sys.exit(1)

    candidates = []
    errors = []

    with ThreadPoolExecutor(max_workers=len(sources)) as ex:
        futures = {
            ex.submit(SOURCE_FUNCTIONS[s], args.query, args.limit, args.timeout): s
            for s in sources
        }
        for f in as_completed(futures, timeout=args.timeout * 2):
            src = futures[f]
            try:
                src_candidates = f.result(timeout=args.timeout + 2)
                candidates.extend(src_candidates)
            except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
                errors.append({"source": src, "error": f"network: {type(e).__name__}: {str(e)[:80]}"})
            except Exception as e:
                errors.append({"source": src, "error": f"{type(e).__name__}: {str(e)[:120]}"})

    result = {
        "status": "ok" if candidates else ("partial" if errors else "empty"),
        "query": args.query,
        "sources_attempted": sources,
        "sources_succeeded": sorted({c["_source"] for c in candidates}),
        "candidates_count": len(candidates),
        "errors": errors,
        "candidates": candidates,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
