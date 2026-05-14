# SkillLens 官方评分 · Benchmark Radar v0.1.0

> 用 [SkillLens](https://github.com/AndrewNgGirl/SkillLens) 官方 CLI 评测
> Mode: **agent-side deep review** · Certificate: **verified**
> Engine: `skilllens-python-cli` v0.2.0 · Rubric hash: `5e5a124282f8cf33`

## 最终得分

| 项目 | 得分 | 等级 |
|---|---|---|
| **总分** | **94.34 / 100** | **S（卓越）** |

## 五大支柱拆解

| 支柱 | 权重 | 得分 | 比率 |
|---|---|---|---|
| Skill 价值（business_value） | 25 | 22.50 | 90.0% |
| 市场竞争力（market） | 15 | 14.06 | 93.7% |
| 运行成本（runtime_cost） | 15 | 14.60 | 97.3% |
| 效果稳定性（reliability） | 20 | 18.68 | 93.4% |
| 书写规范性（writeup） | 25 | 24.50 | 98.0% |
| **小计** | **100** | **94.34** | **94.3%** |
| Bonus（可移植性） | +5 | +4.76 | 95.2% |

**所有支柱均达到 90%+，无短板**。

## 评分等级映射（SkillLens 官方）

| 分数 | 等级 | 中文 |
|---|---|---|
| ≥ 90 | **S** | **卓越** |
| 80-89 | A | 优秀 |
| 70-79 | B | 良好 |
| 60-69 | C | 及格 |
| < 60 | D | 待改进 |

## 评测流程

按 [SkillLens USAGE.md](https://github.com/AndrewNgGirl/SkillLens/blob/main/skills/skill-scorer/USAGE.md) 官方 agent-side Deep Review 三步流程：

```bash
# Step 1: 生成官方 Deep Review prompt
python3 skills/skill-scorer/scripts/score.py --agent-prompt ./benchmark-radar \
  > .skilllens/agent-deep-review-prompt.md

# Step 2: 由 code agent（Claude）按 prompt 严格输出 JSON
# 结果存为 .skilllens/agent-llm-results.json

# Step 3: 官方 CLI 合并 + 校验 + 输出最终分数
python3 skills/skill-scorer/scripts/score.py \
  --llm-results .skilllens/agent-llm-results.json \
  ./benchmark-radar > .skilllens/final-score.json
```

## Certificate

```json
{
  "deepReviewCertificate": {
    "status": "verified",
    "workflow": "agent-prompt -> agent-llm-results -> official-cli-merge",
    "source": "official SkillLens CLI",
    "engine": "skilllens-python-cli",
    "engineVersion": "0.2.0",
    "rubricHash": "5e5a124282f8cf33",
    "llmComplete": true
  }
}
```

仅 `deepReviewCertificate.status="verified"` 的报告才算官方 SkillLens agent-side Deep Review。

## 原始评分文件

- [.skilllens/agent-deep-review-prompt.md](./.skilllens/agent-deep-review-prompt.md) — 官方生成的评测 prompt
- [.skilllens/agent-llm-results.json](./.skilllens/agent-llm-results.json) — Agent 评估结果（含 ratio / evidence / fix / confidence）
- [.skilllens/final-score.json](./.skilllens/final-score.json) — 官方 CLI 合并后的最终评分 JSON

## 关于评分

SkillLens 是开源的 SKILL.md 评分体系，使用 5 大支柱 × 24 子维度的 rubric v3 标准。本评分通过 agent-side deep review 模式产生 verified certificate，等同于官方 Deep Review 的结果。

---

**评测时间**：2026-05-14
**Skill 版本**：v0.1.0
**评分工具版本**：SkillLens engine v0.2.0
