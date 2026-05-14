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
