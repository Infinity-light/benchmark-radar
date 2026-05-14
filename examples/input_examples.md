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
