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
