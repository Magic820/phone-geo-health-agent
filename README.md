# 📱 phone-geo-health Agent

> 一个基于 [OpenClaw]框架运行的智能 Agent，专注于**手机产品 GEO（生成式引擎优化）健康检查**。
> 当用户告诉agent一个手机型号，agent将验证豆包对这款手机的认知是否与官方目标定位一致，检查该手机再豆包生态GEO中的健康状态，发现偏差并提供可执行优化方案。

> 只专注于豆包生态，通过自动化向豆包（Doubao）发送测试 Query，收集 AI 回答数据进行分析。

---

## 🌟 核心特性

| 特性 | 说明 |
|------|------|
| **🎯 完整 GEO 健康检查** | 5 步工作流：产品画像构建 → Query 生成 → 豆包问答 → 认知分析 → 报告生成 |
| **📊 结构化分析报告** | 生成包含评分、问题分析、优先级优化建议的 Markdown 报告 |
| **🤖 豆包对话自动化** | Playwright + Cookie 持久化，支持单轮/多轮对话、批量提问 |
| **📝 决策阶段框架** | 覆盖认知/推荐、对比、决策三个消费者决策阶段 |
| **🔗 引用来源分析** | 自动提取并分析豆包回答中的引用来源质量 |
| **💡 可执行优化建议** | 基于 GEO 知识库提供 P0/P1/P2 优先级建议 |

---

## 🏗️ 项目架构

```
phone-geo-health/
├── 📄 AGENTS.md              # Agent 行为规范与工作流程
├── 📄 BOOTSTRAP.md           # 首次启动引导
├── 📄 IDENTITY.md            # Agent 身份定义
├── 📄 SOUL.md                # Agent 性格与语气
├── 📄 TOOLS.md               # 工具配置笔记
├── 📄 USER.md                # 用户与产品信息配置
├── 📄 MEMORY.md              # 长期记忆存储
│
└── 📁 skills/
    ├── 📁 phone-geo-health/          # GEO 健康检查主技能
    │   ├── 📄 SKILL.md               # 5 步工作流详细定义
    │   ├── 📁 knowledge/
    │   │   └── 📄 doubao_geo_strategy.md   # 豆包 GEO 策略知识库（手机专用）
    │   └── 📁 templates/
    │       └── 📄 report_template.md       # 健康检查报告模板
    │
    └── 📁 doubao-chat/               # 豆包网页对话自动化
        ├── 📄 SKILL.md               # 使用文档与参数说明
        └── 📁 scripts/
            ├── 📄 chat.py            # 核心对话脚本（支持 standalone/CDP 双模式）
            └── 📄 ensure_chrome.py   # Chrome 环境检查
```

---

## 🚀 快速开始   OpenClaw/Qclaw Agent（完整功能）

#### 1. 环境准备

```bash
# 1. 安装 OpenClaw（参考官方文档）
# https://github.com/openclaw

# 2. 安装 Python 依赖
pip install playwright
playwright install chromium
```

#### 2. 配置项目

```bash
# 克隆到 OpenClaw 工作区
cd ~/.qclaw/workspace-agent-xxx
git clone https://github.com/Magic820/phone-geo-health-agent.git .
```

#### 3.  开始使用

在 OpenClaw/Qclaw 对话中说："帮我检查一下 [你的手机型号] 的 GEO 健康状况"

---

### 方式二：独立使用 doubao-chat

#### 1. 快速安装

```bash
git clone https://github.com/Magic820/phone-geo-health-agent.git
cd phone-geo-health-agent
pip install playwright
playwright install chromium
```

#### 2. 首次登录

```bash
# 首次运行会弹出浏览器窗口，手动登录豆包
python skills/doubao-chat/scripts/chat.py "测试" --standalone
# Cookie 自动保存到 ~/.doubao-chat/state.json
```

#### 3. 批量提问

```bash
# 创建问题列表
echo "帮我推荐一款轻薄好用的手机" > queries.txt
echo "7000元左右手机推荐" >> queries.txt

# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"
python skills/doubao-chat/scripts/chat.py --questions-file queries.txt --standalone --timeout=180
```

---

## 📋 工作流程详解

### GEO 健康检查（5 步完整流程）

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. 产品画像构建 │ →  │  2. Query 生成  │ →  │  3. 豆包问答   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                              ↓
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  5. 报告生成    │ ←  │  4. 认知分析    │ ←  │  数据收集完成  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Step 1: 产品画像构建
- 识别手机型号
- 构建完整产品画像（品牌、价格段、定位、核心卖点、竞品）
- 用户确认后继续

#### Step 2: Query 生成（覆盖 3 个决策阶段）
- **认知/推荐阶段**（5个）：泛推荐、价位推荐、人群推荐、场景推荐 ×2
- **对比阶段**（2个）：与核心竞品直接对比
- **决策阶段**（3个）：值不值得买、风险疑虑×2

#### Step 3: 豆包问答执行
- 使用 doubao-chat 批量发送 10 个 Query
- 自动收集回答和引用来源

#### Step 4: 认知与表现分析
- 品牌提及率、首推率统计
- 价格/卖点/人群/定位认知一致性评估
- 引用来源质量分析

#### Step 5: 报告生成
- 生成结构化 Markdown 报告
- 包含 P0/P1/P2 优先级优化建议

---

## 🔧 技能文档

### phone-geo-health 技能
详细工作流定义：[skills/phone-geo-health/SKILL.md](skills/phone-geo-health/SKILL.md)

### doubao-chat 技能
完整使用文档：[skills/doubao-chat/SKILL.md](skills/doubao-chat/SKILL.md)

### GEO 策略知识库
手机行业专用优化指南：[skills/phone-geo-health/knowledge/doubao_geo_strategy.md](skills/phone-geo-health/knowledge/doubao_geo_strategy.md)

---

## 💡 使用场景

###  产品动态监控
> **适用**: 定期监控豆包对产品的认知，识别当前问题，进行GEO优化

---

## ⚙️ 配置选项

### doubao-chat 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DOUBAO_STANDALONE` | - | 设为 `1` 启用 standalone 模式 |
| `DOUBAO_CHAT_TIMEOUT` | `120` | 回复等待超时（秒） |
| `DOUBAO_VERBOSE` | - | 设为 `1` 启用调试输出 |
| `DOUBAO_HEADLESS` | - | 设为 `1` 启用无头模式 |

---

## 📄 开源协议

MIT License — 自由使用、修改和分发。

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

**改进方向**:
- 支持更多 AI 平台（ChatGPT、Claude、文心一言等）
- 扩展 GEO 策略知识库
- 优化报告模板和评分算法
- 添加数据可视化图表
- 支持更多产品品类

---

*基于 OpenClaw 框架构建 | 专为手机产品 GEO 优化设计*
