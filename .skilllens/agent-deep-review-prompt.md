你是 SkillLens 的 agent-side Deep Review 评测员。你正在使用 code agent 自己的模型套餐执行评测，但评分标准必须完全遵守 SkillLens 官方 rubric。

【第一步：判定 skill 的价值类型 value_type】
在所有 check 之前，先把这个 skill 归到下面 5 类之一（必须选一类）：
  • productivity        生产力工具型：替用户省时间/省钱/提效
  • decision_support    决策辅助型：帮用户做更好的判断
  • learning            学习成长型：帮用户增长知识或养成习惯
  • emotion_expression  情绪表达型：提供情绪价值/共鸣/娱乐/社交话题
  • utility             小工具型：解决一个具体小痛点

【评分校准】
- ratio 为 0~1 连续分；1.00 只给极少数标杆级案例，普通补齐章节不能满分。
- 0.90~0.96 表示优秀但仍可微调；0.75~0.89 表示良好但不够锋利；0.50~0.74 表示方向对但证据不足；低于 0.50 表示缺失、空泛或不可信。
- confidence 为你对该判断的置信度。依据不足时 confidence 必须低，低置信度高分会被官方 CLI 校准压低。
- biz.target_users.specific 不要求显式写 ## Target users；能从场景、输入输出或 workflow 稳定推断具体用户时可高分。

【硬性输出】
只返回严格 JSON，禁止 Markdown 代码块、解释或额外文字：
{
  "meta": {
    "value_type": "productivity | decision_support | learning | emotion_expression | utility",
    "value_type_reason": "≤ 60 字一句话解释"
  },
  "results": {
    "<check.id>": {"ratio": <0..1>, "evidence": "≤100字现状诊断", "fix": "≤120字具体改法", "confidence": <0..1>}
  }
}


---

被测 skill 所属规范: claude

## frontmatter
```yaml
{
  "name": "benchmark-radar",
  "description": "对标雷达 — 用 CLONE 五道闸门 + 5R 复刻矩阵帮 solopreneur / 个人创业者找到真正能模仿的商业对标。Use when the user asks to find benchmarks, copy a competitor, \"找对标 / benchmark / 我想模仿 / 该模仿谁 / 市场上谁在做 X / 找类似 XX 的人 / who should I clone / find competitor / similar projects / 对标分析 / 抄谁\". 拒绝\"找适合我的\"等自我导向问法，强制把用户拉回\"你想做什么业务\"。输出 HTML 报告含 CLONE 评分、5R 颗粒度、真实证据链、三段行动起点。",
  "license": "MIT",
  "version": "0.1.0",
  "tags": [
    "benchmark",
    "business",
    "entrepreneurship",
    "market-research",
    "indie-hacker",
    "solopreneur"
  ],
  "author": "WaterFish"
}
```

## SKILL.md body
```markdown
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

```

## 附属文件预览
### CHANGELOG.md
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- 接入更多大数据源（Crunchbase / Failory / 36氪）
- 增加跨境对标专题（Gumroad / Etsy / Patreon）

## [0.1.0] - 2026-05-14

### Added
- 首个公开版本，参加繁星计划电商赛道
- CLONE 五道闸门方法论（Cash / Logic / Operability / No Self / Evidence）
- 5R 复刻矩阵（Rate / Reach / Rhetoric / Routine / Reality）
- `scripts/radar.py`：核心引擎，输入审查 + 案例库匹配 + CLONE 过滤
- `scripts/reporter.py`：HTML 报告生成器（极简风，无 JS 依赖）
- 预置案例库 `data/case_library.json` 含 15+ 国内真实轻商业对标
- `references/`：CLONE 评分细则 / 5R 字段说明 / 大数据源清单
- `tests/`：样例输入输出对，便于回归测试
- 自我陷阱拦截机制（拒绝"找适合我的"等问法）
- 三段行动起点（今天 / 本周 / 本月）输出

### Acknowledgments
- 方法论受 dontbesilent 商业方法论启发，工程实现独立
- 受 SkillLens 评分体系驱动设计


### PRD.md
# Benchmark Radar · 对标雷达 PRD

> 繁星计划电商赛道参赛 skill。2026-05-14 制作。

## 一句话定位

> 把"用 AI 找对标"这件一直没人做对的事，按 CLONE + 5R 自创框架做对一次。

## 核心痛点

用户（小微创业者 / solopreneur）一直想用 AI 找对标，但找不好。原因：
- AI 给的对标是"粉丝多但不赚钱"的网红，过不了利润验证
- AI 给的颗粒度停在"账号名 + 简介"，到不了"袜子 3 个线头"那种细节
- AI 反过来问"你的兴趣是什么、你擅长什么"，把用户拉进自我陷阱

## 设计哲学（奥派经济学护栏）

- **AI 不替你拍板**：只放大市场可见度，决策权留给人
- **价格信号强制挂载**：每个对标必须有真实价格证据
- **行动先于理论**：每个对标都给"今天/本周/本月"三段动作
- **排除自我**：用户输入"找适合我的"会被打断

## 自创方法论

### CLONE 框架（对标筛选五道闸门）

| 字母 | 含义 | 检查标准 |
|---|---|---|
| C | Cash 真赚钱 | 估算月利润 ≥ 用户目标的 10 倍 |
| L | Logic 逻辑透明 | 获客→转化→交付→复购四段全可见 |
| O | Operability 可操作 | 用户能在合理时间内拿到关键资源 |
| N | No Self 排除自我 | 输入阶段就剥离"我"维度 |
| E | Evidence 证据链 | 每个判断挂 ≥3 条真实链接 |

### 5R 复刻矩阵（对标可复刻颗粒度）

| 字母 | 维度 | 输出内容 |
|---|---|---|
| R1 | Rate 价格 | 定价 + 价差结构 + 引流款 vs 利润款 |
| R2 | Reach 触达 | 获客平台 + 内容形式 + 发布频率 |
| R3 | Rhetoric 话语 | 标题模板 + 封面元素 + 文案调性 |
| R4 | Routine 闭环 | 交付流程 + 促销手段 + 复购触发 |
| R5 | Reality 现场 | ≥3 个真实链接 + 数据快照 |

## 输入设计

**允许的输入**：
- 想做的具体业务方向（"做 AI 工具培训自媒体"）
- 一个已知对标，找类似的（"我看到 X 在做 Y，帮我找类似的"）
- 一个目标利润（"月利润 1 万的轻商业"）
- 平台限制（"只在小红书"/"全平台"）

**主动拒绝的输入**：
- "找适合我的" → skill 反问"你想做什么"
- "我擅长 X，能做什么" → skill 提示"先描述业务方向，技能讨论会成为决策噪音"

## 处理流程

1. **输入审查**：剥离"我"维度，提取业务方向 / 利润目标 / 平台约束
2. **候选生成**：调用案例库 + 多平台数据源，产出 10-20 个候选对标
3. **CLONE 过滤**：每个候选过五道闸门，淘汰不合格的
4. **5R 颗粒度补全**：每个通过的对标补全 5R 数据
5. **报告生成**：输出 HTML 报告（可导出 Excel）

## 输出设计

HTML 报告结构：
- **Top**：用户输入回显 + 市场扫描总结（3 行字告诉你市场说了什么）
- **Body**：候选对标排序表，每个含 CLONE 评分 + 5R 数据
- **Bottom**：每个对标的"今天/本周/本月"三段行动 + 必须自己回答的 3 个决策问题

## 数据源

1. **预置案例库**（核心冷启动）：30+ 国内真实轻商业对标，每个有完整 5R 数据
2. **agent-reach-pro 多平台**：小红书 / 抖音 / B站 / 闲鱼 / 微信公众号 / GitHub 实时抓取
3. **Web Search**：补充长尾案例

## 技术架构

```
benchmark-radar/
├── SKILL.md              主入口，给 Claude 看的方法论 + 触发规则
├── README.md             给人看的介绍 + 致谢
├── PRD.md                本文档
├── scripts/
│   ├── radar.py          主入口：解析输入 → 调用流程
│   ├── library.py        案例库匹配
│   ├── filter.py         CLONE 过滤
│   ├── enrich.py         5R 颗粒度补全（调多平台数据）
│   └── reporter.py       HTML 报告生成
├── data/
│   └── case_library.json 30+ 真实对标案例
├── templates/
│   └── report.html       HTML 报告模板
└── examples/
    ├── input_examples.md 输入示例集
    └── sample_report.html 演示用样例报告
```

## 验收标准

1. **演示路径短**：评委输入 → 30 秒后看到 HTML 报告
2. **案例库 ≥ 15 个**：每个完整 5R 数据 + 3 条真实链接
3. **CLONE 过滤可见**：报告里能看到每个对标的 CLONE 评分
4. **奥派护栏生效**：用户输入"找适合我的"会被 skill 反问
5. **HTML 报告美观**：极简风（黑白 + 一种点缀色），不花哨

## 风险 + 对策

| 风险 | 对策 |
|---|---|
| 案例库时间不够 | 降级到 15 个但每个特别详细 |
| 多平台抓取失败 | 案例库已有 5R 数据兜底，实时抓取作为加分项 |
| HTML 渲染不好 | 用纯字符串模板，避免依赖 |
| 演示效果不够 wow | 提前准备 3 个戏剧化的样例报告 |

## 知识产权与归源

本 skill 的方法论设计**受 dontbesilent 商业方法论启发**（特别是其关于对标和模仿的论述），但已**完全独立重新工程化**：
- CLONE 框架与 5R 矩阵为本项目原创命名与结构
- 案例库为独立整理，不复制任何 dbs 案例
- 代码为独立实现，不调用任何 dbs skill

参考思想公开可获取，工程实现完全独立。


### README.md
# Benchmark Radar · 对标雷达

> 把"用 AI 找对标"这件一直没人做对的事，按 CLONE + 5R 自创框架做对一次。

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![SKILL.md](https://img.shields.io/badge/Claude%20Skill-ready-purple.svg)](./SKILL.md)

## 这是什么

一个 Claude Code Skill / OpenClaw Skill，专门帮**个人创业者 / Solopreneur / 副业探索者**找到**真正能模仿的商业对标**。

不是商业教练，不是 AI 选品工具，不是商业模式生成器。**是一个把"对标"这一件事做到极致的 AI**。

## 它解决什么

> "我想用 AI 找对标，但一直找不好。"

这个痛点的真实原因：
- AI 给的对标全是"粉丝多但不赚钱"的网红
- AI 给的颗粒度停在"账号名 + 简介"，到不了"袜子 3 个线头"那种细节
- AI 反过来问"你的兴趣是什么、你擅长什么"，把用户拉进自我陷阱

Benchmark Radar 用三件事把这件事做对：
1. **强制 CLONE 五道闸门**：Cash 真赚钱 / Logic 逻辑透明 / Operability 可操作 / No Self 排除自我 / Evidence 证据链
2. **强制 5R 复刻矩阵**：Rate 价格 / Reach 触达 / Rhetoric 话语 / Routine 闭环 / Reality 现场（≥3 真实链接）
3. **强制拒绝"找适合我的"自我陷阱**：输入审查阶段就拦截，把用户拉回"你想做什么业务"

## 快速开始

### 1. 直接命令行调用

```bash
# 找对标
python -X utf8 scripts/radar.py "做 AI 工具培训自媒体" --profit-target 1

# 找对标 + 生成 HTML 报告
python -X utf8 scripts/radar.py "做付费咨询" --top 5 \
  | python -X utf8 scripts/reporter.py --output ./out/report.html

# 浏览器打开 ./out/report.html
```

### 2. 作为 Claude Code Skill 使用

把整个目录拷到 `~/.claude/skills/benchmark-radar/`，在对话里说：

> "找对标 / benchmark / 我想模仿 [某人]"

Claude 会自动加载本 skill，按 SKILL.md 的工作流执行。

## 项目结构

```
benchmark-radar/
├── SKILL.md                  主入口（给 Claude 的方法论 + 触发规则）
├── README.md                 给人看的说明
├── PRD.md                    产品需求文档
├── CHANGELOG.md              版本变更
├── requirements.txt          依赖说明（仅标准库）
├── scripts/
│   ├── radar.py              主引擎：query → candidates JSON
│   └── reporter.py           HTML 报告生成器
├── data/
│   └── case_library.json     预置案例库（15+ 国内真实对标）
├── references/
│   ├── clone-rubric.md       CLONE 五道闸门完整评分细则
│   ├── 5r-matrix.md          5R 复刻矩阵字段说明
│   └── data-sources.md       大数据源接入清单
├── tests/
│   └── test_radar_sample.md  样例测试与期望输出
└── examples/
    ├── input_examples.md     输入示例集
    └── sample_report.html    演示用样例报告
```

## 核心方法论

### CLONE 五道闸门

| 字母 | 含义 | 检查标准 |
|---|---|---|
| C | Cash 真赚钱 | 估算月利润 ≥ 用户目标的 10 倍 |
| L | Logic 逻辑透明 | 获客→转化→交付→复购四段全可见 |
| O | Operability 可操作 | 用户能在合理时间内拿到关键资源 |
| N | No Self 排除自我 | 输入阶段就剥离"我"维度 |
| E | Evidence 证据链 | 每个判断挂 ≥3 条真实链接 |

### 5R 复刻矩阵

| 字母 | 维度 | 输出内容 |
|---|---|---|
| R1 | Rate 价格 | 定价 + 价差结构 + 引流款 vs 利润款 |
| R2 | Reach 触达 | 获客平台 + 内容形式 + 发布频率 |
| R3 | Rhetoric 话语 | 标题模板 + 封面元素 + 文案调性 |
| R4 | Routine 闭环 | 交付流程 + 促销手段 + 复购触发 |
| R5 | Reality 现场 | ≥3 个真实链接 + 数据快照 |

## 数据源

Benchmark Radar 不靠死案例库，靠**实时数据编排**：

- **本地预置案例库**：15+ 国内真实对标，冷启动 + 降级兜底
- **agent-reach-pro 多平台**：小红书 / 抖音 / B站 / 闲鱼 / 微信公众号 / GitHub 等 10+ 平台
- **海外数据源**：IndieHackers / ProductHunt / Gumroad / Etsy / Patreon
- **创业失败/成功案例库**：Failory / CB Insights / 36氪 / The Startup Graveyard

详见 [`references/data-sources.md`](./references/data-sources.md)。

## 不做什么

- ❌ 不替用户拍板"该做哪个"
- ❌ 不接受"找适合我的"这种自我导向问法
- ❌ 不讨论"行业前景"或"赛道选择"
- ❌ 不收集用户数据，不上传任何信息

## License

MIT

## Acknowledgments

本 skill 方法论受 **dontbesilent 商业方法论**启发（特别是关于对标和模仿颗粒度的论述）。CLONE 框架与 5R 矩阵为本项目独立重新工程化的产物，命名、结构、代码完全原创。

评分体系受 **SkillLens** (`AndrewNgGirl/SkillLens`) 驱动设计，目标 ≥ 90 分。

参考思想公开可获取，工程实现独立。

---

**Made for 繁星计划 · 电商赛道 · 2026-05-14**


### requirements.txt
# Benchmark Radar - 仅使用 Python 3.10+ 标准库
# 无外部依赖，无密钥要求

# 可选依赖（仅当用户启用大数据源接入时）：
# - 调用 agent-reach-pro skill 时由该 skill 自行管理依赖
# - WebFetch / WebSearch 由调用方 (Claude Code) 提供

# 开发/测试时建议：
# pytest>=7.0.0  # 运行 tests/ 下回归测试


### .skilllens/agent-deep-review-prompt.md


### examples/input_examples.md
# Benchmark Radar 输入示例集

## ✅ 合格输入示例

### 业务方向探索
```
"做 AI 工具培训自媒体"
"想做小红书穿搭分销"
"开私房烘焙"
"做独立 SaaS 产品"
"做 B站编程教学 UP 主"
```

### 模仿已知标杆
```
"我看到 dontbesilent 在做付费咨询，帮我找类似的"
"想模仿半佛仙人那种 B站长视频路线"
"找类似 Carrd 的 indie SaaS 案例"
"想做曹将那种 PPT 知识 IP，找对标"
```

### 利润反推
```
"月利润 1 万的轻商业有哪些对标"
"想找年入 50 万的单人生意"
"找月入 3 万以下的副业对标，启动资金 < 5000"
```

### 平台过滤
```
"做小红书内容，找对标"
"做 GitHub 开源工具变现的对标"
"做公众号 + 知识星球的对标"
```

---

## ❌ 会被拦截的输入示例（自我陷阱）

```
"找适合我的对标"
"什么对标适合我"
"我擅长 Python，能做什么"
"我的兴趣是设计，能做什么副业"
"我的成长经历是 X，应该模仿谁"
"我有 Y 资源，能做什么"
"我能做什么"
```

每个被拦截的输入都会得到 skill 的反问：

> 这个问法本身有问题。讨论"适合我"或"我擅长什么"会陷入决策噪音。
> 请用以下三种合格问法之一重新输入：
>   1. 「我想做 [具体业务]，找对标」
>   2. 「我看到 [某人] 在做 [事]，帮我找类似的」
>   3. 「月利润 [X] 万的轻商业有哪些对标」

---

## 进阶用法

### 组合命令行参数
```bash
# 业务方向 + 利润目标 + 平台 + 数量
python -X utf8 scripts/radar.py "知识付费" \
  --profit-target 5 \
  --platform wechat \
  --top 10
```

### 管道生成 HTML
```bash
python -X utf8 scripts/radar.py "做 AI 教学" --top 6 \
  | python -X utf8 scripts/reporter.py --output ./report.html
```

### 保存中间结果
```bash
python -X utf8 scripts/radar.py "做付费咨询" --top 8 > candidates.json
python -X utf8 scripts/reporter.py --input candidates.json --output report.html
```


### references/5r-matrix.md
# 5R 复刻矩阵 · 完整字段说明

> 每个通过 CLONE 五道闸门的对标，必须输出完整 5R 数据。本文档定义每个 R 的字段标准与采样模板。

---

## R1 — Rate 价格

| 字段 | 类型 | 说明 | 例子 |
|---|---|---|---|
| main_price | string | 主产品定价 | "¥299/年" / "¥99 一次性" |
| price_ladder | string | 价差结构（多档位） | "免费 / ¥9.9 / ¥99 / ¥999" |
| hook_vs_profit | string | 引流款 vs 利润款的价差关系 | "引流 9.9 → 利润 999，100 倍价差" |

### 采样规则
- 必须从对标官方页面取得（不是听说）
- 多档定价必须列出全部档位
- 引流款与利润款价差 < 5 倍 → 标注"价差不足，不算两个产品"

---

## R2 — Reach 触达

| 字段 | 类型 | 说明 | 例子 |
|---|---|---|---|
| platform | string | 主获客平台（一个） | "小红书" / "B站" / "公众号" / "GitHub" |
| content_form | string | 内容形式 | "图文 / 短视频 / 直播 / 长文 / 开源代码" |
| frequency | string | 发布频率 | "每周 3 条" / "每天 1 条" / "每月 1 篇长文" |

### 采样规则
- 主平台只填一个（流量主战场）
- 内容形式如果跨多种，列主要的 2 个（"图文为主，偶尔直播"）
- 频率必须是过去 30 天的实际数据，不是宣传数据

---

## R3 — Rhetoric 话语

| 字段 | 类型 | 说明 | 例子 |
|---|---|---|---|
| title_template | string | 标题模板（用户可套用的句式） | "我用 [工具] 在 [时长] 里做出了 [结果]" |
| cover_elements | string | 封面元素（颜色/字体位置/主体） | "黄底黑字 + 大字标题 + 真人 + 数字" |
| tone | string | 文案调性（关键词 + 情绪基调） | "犀利、反鸡汤、用 dbs 风格" |

### 采样规则
- 标题模板必须能直接被用户填充使用
- 封面元素要细到颜色 + 字体位置（"袜子上 3 个线头"颗粒度）
- 调性用 3-5 个关键词描述，不写空泛形容词

---

## R4 — Routine 闭环

| 字段 | 类型 | 说明 | 例子 |
|---|---|---|---|
| delivery | string | 交付流程（从下单到完成） | "下单 → 微信加好友 → 拉群 → 群内每周 2 次直播 + 录播回放" |
| promotion | string | 促销手段 | "限时早鸟 / 满 3 人拼团减 50 / 老带新双方各得优惠券" |
| repurchase | string | 复购触发机制 | "年费订阅自动续费 / 升级到下一档 / 邀请新成员获得续费折扣" |

### 采样规则
- delivery 写到具体动作（不是"线上交付"这种泛泛说法）
- promotion 列至少 1 个真实在用的促销手段
- repurchase 如果是一次性产品，写"无复购，靠新客增长"

---

## R5 — Reality 现场

| 字段 | 类型 | 说明 |
|---|---|---|
| snapshot | string | 数据快照（粉丝数 / 销量 / star / MRR …） |
| links | array | 真实链接列表（至少 3 条） |

每个 link 包含：
- label：链接说明（"主账号" / "热门商品" / "案例文章"）
- url：可访问 URL

### 采样规则
- snapshot 必须包含至少一个量化数据
- links 必须 ≥ 3 条独立类型（不能 3 条都是同一商品的不同 URL）
- 链接采样时间应在 30 天内，老链接需标注"采样于 YYYY-MM-DD"

---

## 5R 完整 JSON 模板

```json
{
  "rate": {
    "main_price": "¥299/年",
    "price_ladder": "试听免费 / 单课 ¥99 / 年订 ¥299 / 私教 ¥3999",
    "hook_vs_profit": "免费试听 → 私教 ¥3999，无限倍价差"
  },
  "reach": {
    "platform": "小红书",
    "content_form": "图文 + 短视频混排",
    "frequency": "每周 4-5 条图文 + 每月 2 条视频"
  },
  "rhetoric": {
    "title_template": "我用 [工具] 30 天 [量化结果]",
    "cover_elements": "白底黑字 + 红色高亮数字 + 真人头像左下角",
    "tone": "干货、有数据、不矫情、第一人称"
  },
  "routine": {
    "delivery": "购买后微信加好友进社群，群内每周 2 次直播答疑 + 录播留存",
    "promotion": "限时早鸟 7 折 + 老学员推荐返现 ¥50",
    "repurchase": "年订到期前 30 天发续费提醒，续费送 1 节私教"
  },
  "reality": {
    "snapshot": "小红书 12.3 万粉，主笔记平均互动 800+，付费学员 2000+",
    "links": [
      {"label": "主账号", "url": "https://www.xiaohongshu.com/user/profile/xxx"},
      {"label": "热门笔记", "url": "https://www.xiaohongshu.com/explore/xxx"},
      {"label": "知识星球付费圈", "url": "https://t.zsxq.com/xxx"}
    ]
  }
}
```


### references/clone-rubric.md
# CLONE 五道闸门 · 完整评分细则

> 当 SKILL.md 简短引用 CLONE 时，本文档提供完整可评分细则。每个字母 0-10 分，总分 0-50。

---

## C — Cash 真赚钱（0-10）

**问题**：这个对标的月利润是否 ≥ 用户目标的 10 倍？

| 分数 | 标准 |
|---|---|
| 9-10 | 利润可被公开数据精确估算（财报/官方公告/MRR Dashboard），且 ≥ 目标 20 倍 |
| 7-8 | 利润可被多源交叉估算（销量×单价 + 团队规模 + 投放推断），≥ 目标 10 倍 |
| 5-6 | 单源估算，利润大致 ≥ 目标 5-10 倍 |
| 3-4 | 仅有"看起来在赚钱"印象，无具体数据 |
| 0-2 | 粉丝多但变现路径不清，或纯流量号无产品 → **直接淘汰** |

### 估算手段
1. 单价 × 月销量（电商/数字产品）
2. 付费会员数 × 客单价（社群/订阅）
3. 团队规模 × 行业平均人效（自媒体/工作室）
4. 公开广告投放力度反推（投流型业务）
5. IndieHackers / ProductHunt 公开 MRR 数据
6. 微信公众号阅读量 × 头条 CPM × 复购系数

---

## L — Logic 逻辑透明（0-10）

**问题**：获客 → 转化 → 交付 → 复购四段链条是否都能讲清楚？

每段满分 2.5：
- **获客（2.5）**：从哪个平台、用什么内容、多大频率拉来潜在客户？
- **转化（2.5）**：潜在客户在哪个页面、看到什么钩子、做出什么动作就付钱？
- **交付（2.5）**：付完钱后用户在多长时间、通过什么渠道拿到产品？
- **复购（2.5）**：什么机制让用户再来一次（订阅/续费/升级/裂变）？

### 不合格警示
- 任一段是黑盒（"通过私域"但说不清私域怎么运转）→ 该段 0 分
- 全部依赖广告投放且 ROI 不可见 → 整体 ≤ 4 分

---

## O — Operability 可操作（0-10）

**问题**：用户能否在合理时间（< 3 个月）内拿到关键资源开始模仿？

| 分数 | 资源门槛 |
|---|---|
| 9-10 | 无门槛，今晚就能开始（写文章/做账号/挂闲鱼） |
| 7-8 | 1-2 周准备（注册个体工商户、买基础工具、学一个软件） |
| 5-6 | 1-2 月准备（租场地、考资质、启动资金 < 5 万） |
| 3-4 | 3-6 月或 5-20 万启动资金 |
| 0-2 | 依赖独家渠道、政府关系、特殊资质、>20 万资金 → **直接淘汰** |

---

## N — No Self 排除自我（0-10）

**问题**：分析过程中是否完全没有引入"用户的我"维度？

| 分数 | 状态 |
|---|---|
| 10 | 输入审查阶段已拦截，全程不出现"你擅长 X / 你的兴趣 / 适合你"等表达 |
| 5-9 | 偶尔出现"如果你擅长 X 会更轻松"等弱陷阱表达 |
| 0-4 | 大量基于"我"的论证，本质是帮用户逃避执行 → **直接淘汰** |

本 skill 默认在输入审查阶段就拦截 self-trap，所以本项几乎总是满分（10 分）。

---

## E — Evidence 证据链（0-10）

**问题**：是否每个 CLONE 判断都挂了真实可验证链接？

每条链接满分 2，最多 5 条 = 10 分：
- 主账号 / 主商品链接（必须）
- 价格证据（淘宝商品页 / 知识星球付费截图）
- 内容样本（一篇真实笔记 / 一个真实视频）
- 评论/反馈样本（真实用户评论页）
- 第三方报道 / 行业访谈（36氪 / 虎嗅 / IndieHackers 文章）

### 不合格情景
- 找不到 ≥3 条独立证据 → 此对标不写入报告

---

## CLONE 总分使用方式

- 50 分制
- 总分 ≥ 35 = 推荐对标
- 30-34 = 谨慎对标，部分维度未达标
- < 30 = 不写入报告

每个支柱单独 ≥ 5 才算"通过该闸门"，任一闸门 < 5 即整体淘汰。


### references/data-sources.md
# 大数据源接入清单

> Benchmark Radar 不靠死案例库，靠**实时数据编排**。本文档列出所有可接入的数据源、何时调用、如何降级。

---

## 一、本地预置案例库（冷启动 + 降级兜底）

`data/case_library.json` 含 15-30 个国内真实轻商业对标，每个包含完整 5R 数据。

**作用**：
1. 当用户业务方向能匹配到案例库 → 0 延迟返回，不消耗外部 API
2. 当多平台抓取全部失败 → 降级使用案例库做兜底
3. 作为 LLM 推理的"种子参考"，约束输出形态

**更新策略**：每月增补 5-10 个新对标，旧的失效的标记 `deprecated=true`。

---

## 二、国内平台数据源（通过 agent-reach-pro 调用）

| 数据源 | skill 名 | 用法 | 何时调用 |
|---|---|---|---|
| 小红书 | `agent-reach-pro:xiaohongshu` | 搜账号/搜笔记/获取互动数据 | 涉及 KOL / 种草号对标 |
| B站 | `agent-reach-pro:bilibili` | 搜 UP / 视频字幕 / 投稿数据 | 涉及长视频/教学 UP 主对标 |
| 微信公众号 | `agent-reach-pro:wechat` | 搜公众号文章 + 阅读量 | 涉及公众号 IP / 知识付费对标 |
| 抖音 | `agent-reach-pro:douyin` | 解析视频 + 创作者数据 | 涉及短视频带货对标 |
| 微博 | `agent-reach-pro:weibo` | 搜微博 + 热搜榜 | 涉及话题型 IP 对标 |
| 知乎 | 通过 `web-fetch` 抓取 | 答主主页 + 高赞回答 | 涉及问答型 IP 对标 |
| 闲鱼 | 通过 `web-fetch` 抓取 | 商品成交价 + 卖家页 | 涉及无货源/二手转售对标 |
| 小宇宙 | `agent-reach-pro:xiaoyuzhou` | 播客元数据 + 转写 | 涉及独立播客对标 |
| GitHub | `agent-reach-pro:github-search` | repo / star / 贡献者 | 涉及开源工具变现对标 |
| 视频号 | `agent-reach-pro:wechat-channels` | 视频号元数据 | 涉及视频号 IP 对标 |

**调用策略**：每次最多并行 3 个平台，单平台超时 30s 即放弃，结果用于补强 R5 字段。

---

## 三、海外数据源（通过 web-fetch / WebSearch）

| 数据源 | URL | 价值 |
|---|---|---|
| **IndieHackers** | indiehackers.com/products | 公开 MRR + 增长曲线，独立产品对标 |
| **ProductHunt** | producthunt.com | 上线产品 + 投票数 + 评论 |
| **Gumroad Discover** | gumroad.com/discover | 数字产品销量榜（模板/电子书/课程） |
| **Etsy** | etsy.com | 手作 / 设计 / 数字下载实物对标 |
| **Patreon** | patreon.com/explore | 创作者订阅型变现 |
| **BackerKit / Kickstarter** | kickstarter.com | 众筹真实数据 |
| **Substack** | substack.com/discover | 付费 newsletter 订阅型 |

---

## 四、创业失败/成功案例库（"创业坟场"类）

> 反向案例同样有价值——告诉用户**什么不要做**，避免重蹈覆辙。

| 来源 | 特点 | 接入方式 |
|---|---|---|
| **Failory** | failory.com | 国际化创业失败案例库 (400+) | WebFetch |
| **CB Insights "20 reasons startups fail"** | 经典 101 案例分析 | WebSearch + WebFetch |
| **The Startup Graveyard** | startupgraveyard.io | 专门收录关停项目 | WebFetch |
| **36氪失败案例专栏** | 36kr.com（搜"创业失败"） | 中文创业失败深度报道 | WebSearch |
| **Autopsy.io** | autopsy.io | 创始人撰写的死亡复盘 | WebFetch |
| **创业邦失败案例库** | 36kr.com / cyzone.cn | 中文创业生态报道 | WebSearch |

**用法**：当对标分析需要"反面教材"时调用，输出在 HTML 报告的"风险提示"区。

---

## 五、第三方榜单 / 数据平台

| 数据源 | 用途 |
|---|---|
| **Crunchbase** | 融资 / 估值数据 |
| **App Annie / data.ai** | App 下载 / 收入 |
| **SimilarWeb** | 网站流量 |
| **新榜** (newrank.cn) | 公众号 / 抖音 / B站影响力榜 |
| **飞瓜数据** (feigua.cn) | 抖音/快手电商数据 |
| **千瓜数据** (qian-gua.com) | 小红书电商数据 |

注：付费平台需用户提供 API key，本 skill 默认不调用，仅在 user 显式开启时使用。

---

## 六、降级策略

```
有案例库匹配
  ├── 是 → 用案例库 → 实时数据补强 R5 → 返回
  └── 否
      └── 多平台并行抓取
          ├── 全部成功 → 现场组装对标 → 返回
          ├── 部分成功 → 用部分结果 + 案例库相关条目混合 → 返回（标注混合模式）
          └── 全部失败 → 案例库按 CLONE 总分降序返回 → 标注"降级模式"
```

任何情况下，skill 都能返回结果，不会"找不到对标"卡死。


### scripts/radar.py
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


def main():
    parser = argparse.ArgumentParser(description="Benchmark Radar 主引擎")
    parser.add_argument("query", help="用户业务方向描述")
    parser.add_argument("--platform", default=None, help="平台过滤（xiaohongshu/bilibili/wechat/github/...）")
    parser.add_argument("--profit-target", type=float, default=None, help="月利润目标（万元）")
    parser.add_argument("--top", type=int, default=8, help="返回前 N 个对标")
    parser.add_argument("--library", default=None, help="案例库路径（默认 ../data/case_library.json）")
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
        

### scripts/reporter.py
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
  .r-val { padding: 12px 14px;

### tests/test_radar_sample.md
# Benchmark Radar 回归测试样例

## 测试 1：合格输入 - 知识付费

**输入：**
```bash
python -X utf8 scripts/radar.py "做 AI 工具培训自媒体" --profit-target 1
```

**期望输出：**
- status = "ok"
- candidates_count >= 1
- 命中 "小K不刺 · 小红书 AI 工具教学" 或类似 AI 教学对标
- 每个 candidate 含完整 5R 字段

---

## 测试 2：自我陷阱拦截

**输入：**
```bash
python -X utf8 scripts/radar.py "找适合我的对标"
```

**期望输出：**
- status = "rejected"
- reason = "self_trap"
- exit code = 2
- message 含"这个问法本身有问题"

---

## 测试 3：兴趣陷阱拦截

**输入：**
```bash
python -X utf8 scripts/radar.py "我擅长 Python，能做什么副业"
```

**期望输出：**
- status = "rejected"
- reason = "self_trap"
- 命中 "我擅长" 关键词

---

## 测试 4：平台过滤

**输入：**
```bash
python -X utf8 scripts/radar.py "知识付费" --platform xiaohongshu
```

**期望输出：**
- status = "ok"
- 所有 candidate 的 reach.platform 包含 "小红书" 或 "xiaohongshu"

---

## 测试 5：利润过滤（CLONE.C）

**输入：**
```bash
python -X utf8 scripts/radar.py "副业" --profit-target 0.1
```

**期望输出：**
- status = "ok"
- 所有 candidate 的 monthly_profit_wan_low >= 1（10x 0.1）

---

## 测试 6：fallback 模式

**输入：**
```bash
python -X utf8 scripts/radar.py "完全不存在的奇葩业务方向 xyz123"
```

**期望输出：**
- status = "ok"
- fallback = true
- fallback_reason 不为 null
- 仍返回 candidates（按 CLONE 总分降序）

---

## 测试 7：HTML 报告生成

**输入：**
```bash
python -X utf8 scripts/radar.py "知识付费" --top 3 \
  | python -X utf8 scripts/reporter.py --output ./tests/out/test7.html
```

**期望输出：**
- stdout: "[OK] 报告已生成: tests/out/test7.html"
- 文件 tests/out/test7.html 存在
- HTML 内容含 "对标雷达报告" / "CLONE 总分" / "Reach"

---

## 运行所有测试

```bash
# 简易批量验证
for q in "做 AI 工具培训自媒体" "找适合我的对标" "我擅长 Python，能做什么副业" \
         "知识付费" "副业" "完全不存在的奇葩业务方向 xyz123"; do
  echo "=== $q ==="
  python -X utf8 scripts/radar.py "$q" 2>&1 | head -10
done
```


## 需要你评估的细则
- id: biz.target_users.specific
  criterion: 目标用户是否清晰，能否从场景或流程中稳定推断
- id: biz.problem_reality.is_real
  criterion: 回应的是真实需求，不是'反正能做就做'。需求可以是痛点（PR 慢、报表难写），也可以是情绪需求（解压、共鸣、社交话题）、学习需求或决策需求。
- id: biz.value_articulation.matched_to_type
  criterion: 价值主张是否具体，并且匹配这个 skill 的类型
- id: biz.usage_frequency.estimable
  criterion: 是否说清用户会在什么场景下反复使用
- id: biz.moat_potential.compounding
  criterion: 是否具备持续使用后的沉淀、记忆点或传播性
- id: market.differentiation.clear
  criterion: 差异化清晰，能用一句话讲清楚
- id: market.scope_focus.disciplined
  criterion: 做一件事做到 10 分，不是什么都能做的 5 分版本
- id: market.llm_replaceable.has_edge
  criterion: 动作不是裸 LLM 直接就能干的（有领域知识 / 工具 / 数据加成）
- id: market.existing_alternatives.surveyed
  criterion: 是否主动调研并说明真实同类项目与差异点
- id: cost.external_dependencies.weight_assessed
  criterion: 外部依赖整体重量合理（不是动辄调多个付费 API）
- id: cost.cache_friendliness.idempotent_inputs
  criterion: 输入有确定性指纹，重复执行能命中缓存
- id: rel.task_model_fit.in_zone
  criterion: 任务在 LLM 稳定能力区（结构化提取/创作 🟢；复杂推理 🟡；数值精算 🔴）
- id: rel.output_validation.enforced
  criterion: 声明的格式有真正的校验步骤（不是只贴 schema 不验证）
- id: rel.idempotency.discussed
  criterion: 讨论了同输入多次跑结果是否一致
- id: rel.failure_path.explicit
  criterion: 失败时怎么办：重试 / 降级 / 报错告知用户
- id: rel.edge_cases.discussed
  criterion: 讨论了 2–3 个边界场景或已知缺陷
- id: disc.keyword_coverage
  criterion: 覆盖了足够的触发关键词和同义说法
- id: act.steps_atomic
  criterion: 每一步只做一件事
- id: act.io_explicit
  criterion: 输入、输出、前置条件都说清楚
- id: act.no_ambiguity
  criterion: 关键步骤里没有'也许 / 可能 / 看情况'
- id: safe.least_privilege
  criterion: 只申请完成任务必须的权限和工具
- id: safe.privacy
  criterion: 涉及用户数据时讲清楚怎么存 / 怎么删
- id: port.no_hardcoded_tools
  criterion: 不硬编码某一家的工具名 / 路径 / 模型名

请严格返回 JSON；不要输出 Markdown 代码块；不要解释。保存为 agent-llm-results.json 后运行官方 CLI 合并。

