# Benchmark Radar · 对标雷达

> 把"用 AI 找对标"这件一直没人做对的事，按 CLONE + 5R 自创框架做对一次。

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![SKILL.md](https://img.shields.io/badge/Claude%20Skill-ready-purple.svg)](./SKILL.md)
[![SkillLens](https://img.shields.io/badge/SkillLens-94.34%2F100%20%C2%B7%20S-gold.svg)](./SKILLLENS_SCORE.md)

> 🏆 **SkillLens 官方评测：94.34 / 100，等级 S（卓越）** · [详细评分报告](./SKILLLENS_SCORE.md) · Certificate verified

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
