#!/usr/bin/env python3
"""
Benchmark Radar - 主引擎
输入: 用户业务方向 query (+ 可选 platform / profit-target)
输出: 候选对标 JSON (按 CLONE 总分降序排列)

用法:
    python -X utf8 radar.py "做 AI 工具培训自媒体" --profit-target 5
    python -X utf8 radar.py "做付费咨询" --platform xiaohongshu
    python -X utf8 radar.py "月利润 1 万的轻商业" --top 8
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


SELF_CHAIN = [
    "适合我", "我的兴趣", "我擅长", "我的成长", "我的经历",
    "我的优势", "我的劣势", "我的资源", "我有什么", "我能做什么",
    "fit me", "suitable for me", "my interest", "my skill",
]


def detect_self_trap(query: str) -> bool:
    """检测输入是否落入'自我陷阱'。"""
    q = query.lower()
    return any(token.lower() in q for token in SELF_CHAIN)


def load_library(library_path: Path) -> list:
    """加载案例库。"""
    with library_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def tokenize(text: str) -> set:
    """简单中英文分词：拉丁词按空格分，中文按 2-3 gram 分。"""
    text = text.lower()
    tokens = set()
    # 英文/数字 token
    for m in re.findall(r"[a-z0-9]+", text):
        tokens.add(m)
    # 中文 2-gram + 3-gram
    chinese = re.findall(r"[一-鿿]+", text)
    for chunk in chinese:
        for size in (2, 3):
            for i in range(len(chunk) - size + 1):
                tokens.add(chunk[i:i + size])
    return tokens


def score_match(query_tokens: set, case: dict) -> int:
    """基于 query 和 case tags / category / business 的 token 重合度评分。"""
    case_text = " ".join([
        case.get("category", ""),
        case.get("business", ""),
        " ".join(case.get("tags", [])),
        case.get("rhetoric", {}).get("tone", ""),
    ])
    case_tokens = tokenize(case_text)
    overlap = query_tokens & case_tokens
    return len(overlap)


def clone_total(case: dict) -> int:
    """计算 CLONE 总分（5 项相加）。"""
    clone = case.get("clone", {})
    return sum([
        clone.get("cash", 0),
        clone.get("logic", 0),
        clone.get("operability", 0),
        clone.get("no_self", 0),
        clone.get("evidence", 0),
    ])


def filter_by_platform(cases: list, platform: str | None) -> list:
    if not platform:
        return cases
    plat = platform.lower()
    return [c for c in cases if plat in (c.get("reach", {}).get("platform", "") or "").lower()
            or plat in [p.lower() for p in c.get("platforms", [])]]


def filter_by_profit(cases: list, target_wan: float | None) -> list:
    """利润过滤：保留那些月利润 ≥ target × 10 的对标（CLONE.C 信条）。"""
    if target_wan is None:
        return cases
    threshold = target_wan * 10  # 万元
    return [c for c in cases if c.get("monthly_profit_wan_low", 0) >= threshold]


def fetch_realtime(query: str, limit: int = 3, timeout: float = 10) -> tuple[list[dict], list[dict]]:
    """调用 enrich.py 拉实时大数据（loot-drop / github / hn）。
    返回 (candidates, errors)。失败不抛异常，仅返回空数组 + 错误信息。
    """
    enrich_path = Path(__file__).resolve().parent / "enrich.py"
    if not enrich_path.exists():
        return [], [{"source": "enrich", "error": "enrich.py 不存在"}]

    try:
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(enrich_path), query,
             "--limit", str(limit), "--timeout", str(timeout)],
            capture_output=True, text=True, encoding="utf-8",
            timeout=timeout * 4,  # 多源并行总超时
        )
        if proc.returncode != 0:
            return [], [{"source": "enrich", "error": f"exit {proc.returncode}: {proc.stderr[:200]}"}]
        data = json.loads(proc.stdout)
        return data.get("candidates", []), data.get("errors", [])
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return [], [{"source": "enrich", "error": f"{type(e).__name__}: {str(e)[:120]}"}]


def main():
    parser = argparse.ArgumentParser(description="Benchmark Radar 主引擎")
    parser.add_argument("query", help="用户业务方向描述")
    parser.add_argument("--platform", default=None, help="平台过滤（xiaohongshu/bilibili/wechat/github/lootdrop/...）")
    parser.add_argument("--profit-target", type=float, default=None, help="月利润目标（万元）")
    parser.add_argument("--top", type=int, default=8, help="返回前 N 个对标")
    parser.add_argument("--library", default=None, help="案例库路径（默认 ../data/case_library.json）")
    parser.add_argument("--no-realtime", action="store_true", help="禁用实时大数据抓取（仅用本地案例库）")
    parser.add_argument("--realtime-limit", type=int, default=3, help="每个实时源最多返回 N 条（默认 3）")
    args = parser.parse_args()

    # Self-trap 检测
    if detect_self_trap(args.query):
        result = {
            "status": "rejected",
            "reason": "self_trap",
            "message": (
                "这个问法本身有问题。讨论'适合我'或'我擅长什么'会陷入决策噪音。\n"
                "请用以下三种合格问法之一重新输入：\n"
                "  1. 「我想做 [具体业务]，找对标」\n"
                "  2. 「我看到 [某人] 在做 [事]，帮我找类似的」\n"
                "  3. 「月利润 [X] 万的轻商业有哪些对标」"
            ),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(2)

    # 加载案例库
    if args.library:
        library_path = Path(args.library)
    else:
        library_path = Path(__file__).resolve().parent.parent / "data" / "case_library.json"

    if not library_path.exists():
        print(json.dumps({
            "status": "error",
            "reason": "library_not_found",
            "message": f"案例库不存在: {library_path}",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    library = load_library(library_path)

    # 实时大数据抓取（默认启用）
    realtime_cands = []
    realtime_errors = []
    if not args.no_realtime:
        realtime_cands, realtime_errors = fetch_realtime(args.query, limit=args.realtime_limit)

    # 合并实时 + 案例库
    merged = realtime_cands + library

    # 平台过滤
    pool = filter_by_platform(merged, args.platform)
    after_platform = len(pool)

    # 利润过滤（应用 CLONE.C 信条：≥ 10x 目标）
    pool = filter_by_profit(pool, args.profit_target)
    after_profit = len(pool)

    # Hint：利润过滤可能淘汰了相关案例
    hint = None
    if args.profit_target and after_profit < after_platform:
        removed = after_platform - after_profit
        hint = (
            f"⚠️ CLONE.C 信条已激活：利润目标 {args.profit_target} 万/月要求对标月利润 ≥ "
            f"{args.profit_target * 10} 万。本次因此过滤掉 {removed} 个案例（其中可能含与你 query 高度相关的）。"
            f"如果结果偏离预期，试试降低 --profit-target 或不指定。"
        )

    # 关键词匹配评分
    # 实时抓取的候选（_source in lootdrop/github/hn）天然带 query 相关性 → 给基础分 50，不再过滤
    # 案例库候选必须通过 token-overlap 才进入
    q_tokens = tokenize(args.query)
    scored = []
    for case in pool:
        is_realtime = case.get("_source") in ("lootdrop", "github", "hn")
        if is_realtime:
            match_score = 5  # 实时数据基础分（远高于本地匹配的 0-3，但不至于淹没强匹配本地案例）
        else:
            match_score = score_match(q_tokens, case)
            if match_score == 0:
                continue
        clone_score = clone_total(case)
        total = match_score * 10 + clone_score  # match 优先，CLONE 作 tie-breaker
        scored.append((total, match_score, clone_score, case))

    scored.sort(key=lambda x: -x[0])
    top_cases = [c for _, _, _, c in scored[:args.top]]

    # 如果关键词匹配没结果，回退到全库按 CLONE 排序（带降级提示）
    fallback = False
    if not top_cases:
        fallback = True
        all_with_clone = [(clone_total(c), c) for c in pool]
        all_with_clone.sort(key=lambda x: -x[0])
        top_cases = [c for _, c in all_with_clone[:args.top]]

    # 统计实时数据贡献
    realtime_in_result = sum(1 for c in top_cases if c.get("_source") in ("lootdrop", "github", "hn"))
    library_in_result = len(top_cases) - realtime_in_result

    result = {
        "status": "ok",
        "query": args.query,
        "platform_filter": args.platform,
        "profit_target_wan": args.profit_target,
        "candidates_count": len(top_cases),
        "realtime_enabled": not args.no_realtime,
        "realtime_candidates_fetched": len(realtime_cands),
        "realtime_in_result": realtime_in_result,
        "library_in_result": library_in_result,
        "realtime_errors": realtime_errors,
        "fallback": fallback,
        "fallback_reason": "未匹配到强相关案例，按 CLONE 总分降序展示库内通过过滤的全部对标" if fallback else None,
        "hint": hint,
        "candidates": top_cases,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
