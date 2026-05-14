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
