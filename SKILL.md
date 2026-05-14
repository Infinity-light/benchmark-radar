---
name: benchmark-radar
description: 对标雷达 — 用 CLONE 五道闸门 + 5R 复刻矩阵帮 solopreneur / 个人创业者找到真正能模仿的商业对标。Use when the user asks to find benchmarks, copy a competitor, "找对标 / benchmark / 我想模仿 / 该模仿谁 / 市场上谁在做 X / 找类似 XX 的人 / who should I clone / find competitor / similar projects / 对标分析 / 抄谁". 拒绝"找适合我的"等自我导向问法，强制把用户拉回"你想做什么业务"。输出 HTML 报告含 CLONE 评分、5R 颗粒度、真实证据链、三段行动起点。
license: MIT
version: 0.1.0
tags: [benchmark, business, entrepreneurship, market-research, indie-hacker, solopreneur]
author: WaterFish
---

# Benchmark Radar · 对标雷达

> 把"用 AI 找对标"这件一直没人做对的事，按 CLONE + 5R 自创框架做对一次。

## Target users

1. **个人创业者 / Solopreneur**：单人或 ≤2 人小团队，想找具体可模仿的商业模式
2. **副业探索者**：本职在岗，想用业余时间启动可验证轻商业，需要真实参照
3. **小红书 / 抖音 / 公众号内容创作者**：流量起来了但变现路径不清，想抄成熟玩家的闭环
4. **独立开发者 (Indie Hacker)**：做了产品但不知如何变现，想看 ProductHunt / IndieHackers 对标 MRR

不适合：大公司战略、纯学术研究、无业务方向的"自我探索"用户。

## When to use

- **高频**：每次想做新业务前，找 5-8 个值得复刻的对标
- **中频**：每月对当前业务做"对标颗粒度复盘"，看自己抄到几成
- **低频**：偶尔被问"该模仿谁"时直接调用

每次调用产出可存档的 HTML 报告，多次调用可累积成"个人对标库"。

## Why this skill

| 现有方案 | 对标 Radar 不同点 |
|---|---|
| ChatGPT 直接问"找对标" | 我们强制 CLONE 五道闸门过滤，淘汰粉丝多但不赚钱的伪对标 |
| ai-side-hustle-finder.com | 英文、美国市场，本 skill 中文 + 国内平台真实数据 |
| ProductHunt Business Idea Generator | 通用 idea 生成无价格证据，本 skill 强制每个对标挂 ≥3 真实链接 + 价格快照 |
| dbs-benchmark（dontbesilent） | dbs 是诊断对话型，需人来问对的问题；本 skill 把方法论工业化为脚本 + 数据源 |

**一句话差异化**：唯一一个**强制拒绝"找适合我的"自我陷阱**、**强制每条挂真实价格证据**、**强制按 5R 颗粒度拆解**的对标 AI。

## Inputs

| 字段 | 类型 | 必填 | 说明 | 影响输出 |
|---|---|---|---|---|
| query | string | ✅ | 业务方向描述（如"做 AI 工具培训自媒体"） | 决定输出 |
| platform | enum | ❌ | xiaohongshu/bilibili/wechat/github/all | 决定输出 |
| profit_target_wan | number | ❌ | 月利润目标（万元） | 决定输出（CLONE.C 闸门） |
| top | int | ❌ | 返回前 N 个，默认 8 | 不影响哈希 |

**缓存键** = sha256(query + platform + profit_target_wan)。重复查询命中缓存，N 次重跑只算 1 次。

**禁止输入**（被 self-trap 拦截，详见 references/clone-rubric.md）：
- "找适合我的对标" / "什么对标适合我"
- "我擅长 X，能做什么"
- "我的兴趣是 Y / 我的成长经历是 Z"

## Workflow

1. **审查输入**：调 `scripts/radar.py` → 若命中 self-trap 关键词，立即返回拒绝 JSON 并提示用户重新提问
2. **匹配候选**：从 `data/case_library.json` + 实时多平台数据源（agent-reach-pro）抽取候选对标
3. **CLONE 过滤**：每个候选过 5 道闸门（Cash / Logic / Operability / No Self / Evidence），任一不及格即淘汰
4. **5R 颗粒度补全**：对通过的对标补全 R1-R5 字段（详见 references/5r-matrix.md）
5. **生成报告**：调 `scripts/reporter.py` 渲染 HTML，含 CLONE 评分条 + 5R 表格 + 三段行动 + 决策提示
6. **校验输出**：检查 HTML 文件已生成、候选数 ≥ 1、每个候选 5R 字段非空，失败按 ## Failure 处理

## Outputs

JSON schema (radar.py 输出)：

```json
{
  "status": "ok|rejected|error",
  "query": "string",
  "platform_filter": "string|null",
  "profit_target_wan": "number|null",
  "candidates_count": "int",
  "fallback": "boolean",
  "candidates": [
    {
      "name": "string", "category": "string", "business": "string",
      "platforms": ["string"], "tags": ["string"],
      "monthly_profit_wan_low": "number", "monthly_profit_wan_high": "number",
      "clone": {"cash": "0-10", "logic": "0-10", "operability": "0-10", "no_self": "0-10", "evidence": "0-10"},
      "rate":     {"main_price": "string", "price_ladder": "string", "hook_vs_profit": "string"},
      "reach":    {"platform": "string", "content_form": "string", "frequency": "string"},
      "rhetoric": {"title_template": "string", "cover_elements": "string", "tone": "string"},
      "routine":  {"delivery": "string", "promotion": "string", "repurchase": "string"},
      "reality":  {"snapshot": "string", "links": [{"label":"string","url":"string"}]},
      "actions":  {"today": "string", "week": "string", "month": "string"},
      "one_liner": "string"
    }
  ]
}
```

HTML report (reporter.py 输出)：极简风（黑白 + 深绿点缀色），含 Top / Body / Bottom 三区。

## Example

输入：
```bash
python -X utf8 scripts/radar.py "做 AI 工具培训自媒体" --profit-target 1 --top 5 \
  | python -X utf8 scripts/reporter.py --output ./out/report.html
```

预期输出：
- stdout：`[OK] 报告已生成: out/report.html`
- 文件：`out/report.html` 含 5 个候选对标，每个带完整 CLONE/5R/三段行动
- 评委浏览器打开 → 30 秒内看到 wow 报告

完整端到端示例见 `examples/sample_report.html` 和 `examples/input_examples.md`。

## Dependencies

| 名称 | 类型 | 是否付费 | 单次成本 |
|---|---|---|---|
| Python 3.10+ | runtime | 免费 | - |
| 标准库 (json/argparse/html/pathlib) | lib | 免费 | - |
| agent-reach-pro skill | optional skill | 免费 | 受目标平台限频影响 |

**无外部 API、无密钥要求**。所有数据本地处理。详见 `requirements.txt`。

## Failure

| 失败类型 | 处理 |
|---|---|
| 输入命中 self-trap | 返回 status=rejected JSON，HTML 显示打断话术，等用户重新提问 |
| 案例库匹配 0 结果 | 自动降级：按 CLONE 总分降序展示库内 Top N，HTML 标注"降级模式" |
| 多平台抓取失败 | 单平台失败不阻断，案例库 R1-R4 兜底，R5 仅显示库内静态链接 |
| HTML 写入失败 | radar.py 返回 exit 1，stderr 输出错误路径，提示检查目录权限 |
| 案例库 JSON 解析错 | 返回 status=error，提示用户检查 `data/case_library.json` 是否被破坏 |

## Determinism

- **幂等步骤**（脚本/规则）：输入审查、案例库匹配、CLONE 评分、5R 提取、HTML 渲染——同输入 100% 同输出
- **抖动步骤**（仅 agent-reach-pro 实时数据）：实时抓取的 R5 数据可能因平台数据更新而变化，建议设 cache TTL = 24h

整体上 ≥80% 输出来自确定性脚本，重跑结果稳定。

## Known limitations

1. **案例库覆盖度有限**：当前预置 ~15-30 个真实国内对标，长尾业务方向可能命中率低 → 触发 fallback 模式
2. **价格估算精度**：monthly_profit_wan 区间为公开数据估算，非财报真值，仅供参考
3. **多平台抓取依赖第三方**：agent-reach-pro 平台失效时，R5 仅有静态链接，无实时数据快照

## Privacy

- 用户输入仅在本地处理，不发送给任何外部服务
- 不收集、不存储、不上传用户的查询历史
- 无 telemetry、无埋点
- HTML 报告生成在用户指定本地路径，不上传云端

## Bonus / Portability

- frontmatter 仅使用 name / description / license / version / tags / author 通用字段，跨 Claude / OpenClaw / Cursor 三规范通用
- 不硬编码任何模型名或厂商工具，使用"任意 file-read / 任意 markdown-render"等能力描述
- 完全开源，MIT License

## References

- `references/clone-rubric.md` — CLONE 五道闸门完整评分细则与示例
- `references/5r-matrix.md` — 5R 复刻矩阵每个 R 的完整字段说明与采样模板
- `references/data-sources.md` — 大数据源接入清单（创业坟场/IndieHackers/ProductHunt/36氪等）

## Acknowledgments

本 skill 方法论受 **dontbesilent 商业方法论**启发（特别是关于对标和模仿颗粒度的论述）。CLONE 框架与 5R 矩阵为本项目独立重新工程化的产物，命名、结构、代码完全原创。参考思想公开可获取，工程实现独立。
