---
name: doubao-chat
description: >
  通过 Playwright + Chrome CDP 连接已登录的豆包网页端，模拟真实用户发送聊天问题并获取 AI 回复。
  当用户需要向豆包发起提问、与豆包对话、获取豆包回复、测试豆包响应时，应使用此技能。
  支持单轮和多轮对话，返回结构化 JSON 结果。
---

# doubao-chat — 豆包网页对话自动化

## 概述

通过 Playwright 在豆包（doubao.com）网页端模拟真实用户发送问题并获取回复。

**核心特性：**
- 🔑 **一次登录，永久复用** — Cookie 自动保存到 `~/.doubao-chat/state.json`
- 📝 **多问题批量提问** — 支持一次发送多个问题，独立记录每个 Q&A
- 🔗 **引用提取** — 自动提取豆包回复中的参考引用链接

## 两种运行模式

### 模式一：Standalone（推荐）

使用 Playwright 自带的 Chromium 浏览器，自动保存/加载 Cookie 实现会话持久化。

```
问题 → chat.py --standalone → Playwright Chromium → Cookie 持久化 → 豆包 Web → 提取回复+引用 → JSON
```

### 模式二：Chrome CDP

连接已登录的 Chrome 浏览器（需以 `--remote-debugging-port=9222` 启动），直接复用登录态。

```
问题 → chat.py → Playwright CDP → 已登录 Chrome → 豆包 Web → 提取回复+引用 → JSON
```

## 默认触发场景

| 类型 | 示例表述 |
|------|----------|
| **对话提问类** | 问豆包…、让豆包回答…、用豆包查一下…、帮我问豆包… |
| **品牌直达** | 豆包问答、豆包聊天、和豆包对话 |
| **测试验证类** | 测试豆包回复、验证豆包响应 |

### 不触发的情况

- 用户要求用豆包生成图片/视频（应使用 doubao-skills 图片/视频技能）
- 用户只是讨论豆包产品本身，不需要实际对话

## 前置条件

| 模式 | 条件 | 说明 |
|------|------|------|
| Standalone | Python Playwright 已安装 | `pip install playwright && playwright install chromium` |
| Standalone | 首次需手动登录 | 弹出浏览器窗口，登录后自动保存 Cookie，后续无需再登录 |
| CDP | 安装了 Google Chrome | 需要本地 Chrome 浏览器 |
| CDP | Chrome 以调试模式运行 | 需开放端口 9222 |
| CDP | 豆包已在该 Chrome 中登录 | 登录一次后永久有效 |

## 使用流程

### Standalone 模式（推荐）

1. **首次使用**：`python skills/doubao-chat/scripts/chat.py "你的问题" --standalone`
   - 浏览器窗口弹出 → 手动登录豆包 → 自动保存 Cookie
2. **后续使用**：`python skills/doubao-chat/scripts/chat.py "你的问题" --standalone`
   - 自动加载 Cookie，**无需再次登录**
3. 也可设为默认：`set DOUBAO_STANDALONE=1`

### 多问题批量提问

```bash
# 多个问题用空格分隔
python skills/doubao-chat/scripts/chat.py "问题1" "问题2" "问题3" --standalone

# 或从文件读取（每行一个问题）
python skills/doubao-chat/scripts/chat.py -f questions.txt --standalone
```

### CDP 模式

1. 环境检查：`python skills/doubao-chat/scripts/ensure_chrome.py`
2. 发送问题：`python skills/doubao-chat/scripts/chat.py "你的问题"`

## 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `questions` | string(s) | 必填 | 一个或多个问题（空格分隔） |
| `-f, --questions-file` | string | — | 从文件读取问题（每行一个） |
| `--standalone` | flag | 否 | 使用 Playwright 自带 Chromium（推荐） |
| `--headless` | flag | 否 | 无头模式（仅 standalone，需已登录） |
| `--cdp-url` | string | `http://127.0.0.1:9222` | Chrome CDP 地址 |
| `--timeout` | number | `120` | 每个问题等待回复的最长时间（秒） |
| `--new-thread` | flag | 否 | 开启新的对话线程 |
| `--screenshot-dir` | string | 空 | 调试截图保存目录 |
| `--verbose` | flag | 否 | 启用详细调试输出 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DOUBAO_STANDALONE` | 空 | 设为 `1` 默认使用 standalone 模式 |
| `DOUBAO_CDP_URL` | `http://127.0.0.1:9222` | Chrome CDP 地址 |
| `DOUBAO_CHAT_TIMEOUT` | `120` | 默认回复等待超时（秒） |
| `DOUBAO_HEADLESS` | 空 | 设为 `1` 默认使用无头模式 |
| `DOUBAO_VERBOSE` | 空 | 设为 `1` 启用调试输出 |
| `DOUBAO_SCREENSHOT_DIR` | 空 | 调试截图目录 |

## 返回值 JSON 格式

### 单问题成功

```json
{
  "success": true,
  "question": "3000元以下有什么手机推荐？",
  "answer": "3000元以下推荐以下几款手机...",
  "references": [
    {"text": "2026年3000元手机推荐", "url": "https://..."},
    {"text": "小米15 vs iQOO 13对比", "url": "https://..."}
  ],
  "timestamp": "2026-05-24T05:30:00+08:00",
  "meta": {
    "pageUrl": "https://www.doubao.com/thread/...",
    "sendMethod": "button[class*=send]",
    "extractionMethod": "div[class*=markdown]",
    "mode": "standalone"
  }
}
```

### 多问题批量成功

```json
{
  "success": true,
  "results": [
    {
      "success": true,
      "question": "3000元以下有什么手机推荐？",
      "answer": "3000元以下推荐以下几款手机...",
      "references": [
        {"text": "2026年3000元手机推荐", "url": "https://..."}
      ],
      "timestamp": "2026-05-24T05:30:00+08:00",
      "meta": {"extractionMethod": "div[class*=markdown]", "mode": "standalone"}
    }
  ],
  "totalQuestions": 1,
  "successCount": 1,
  "failCount": 0,
  "timestamp": "2026-05-24T05:30:00+08:00",
  "meta": {"mode": "standalone"}
}
```

### 失败

```json
{
  "success": false,
  "error": "NOT_LOGGED_IN",
  "message": "Not logged in to Doubao. Please log in via Chrome first."
}
```

## 错误码

| 错误码 | 原因 | 解决方案 |
|--------|------|----------|
| `CDP_CONNECTION_FAILED` | Chrome CDP 不可连接 | 运行 `ensure_chrome.py` 或使用 `--standalone` |
| `NOT_LOGGED_IN` | 豆包未登录 | 首次使用 standalone 模式会弹出浏览器登录 |
| `INPUT_NOT_FOUND` | 找不到聊天输入框 | 确认页面已加载；豆包 UI 可能变更 |
| `INPUT_FAILED` | 无法输入问题 | 检查输入框是否可交互 |
| `RESPONSE_TIMEOUT` | 等待回复超时 | 增大 `--timeout` 参数 |
| `RESPONSE_EXTRACTION_FAILED` | 回复完成但无法提取文本 | 使用 `--verbose` 调试 |
| `NAVIGATION_FAILED` | 导航到豆包失败 | 检查网络连接 |
| `STANDALONE_LAUNCH_FAILED` | 无法启动 Playwright 浏览器 | 确认 Playwright Chromium 已安装 |
| `PLAYWRIGHT_NOT_INSTALLED` | Playwright 未安装 | `pip install playwright && playwright install chromium` |
| `NO_QUESTIONS` | 未提供问题 | 提供 positional 参数或使用 `--questions-file` |
| `FILE_NOT_FOUND` | 问题文件不存在 | 检查文件路径是否正确 |
| `FILE_READ_ERROR` | 读取问题文件失败 | 检查文件编码是否为 UTF-8 |

## 常见问题与解决

### 问题1：编码乱码（Windows）

**现象**：回答内容显示为乱码（如 `һ�������ᱡ�콢`）或报错 `UnicodeEncodeError: 'gbk' codec can't encode character`

**原因**：Windows 终端默认使用 GBK 编码，而 Python 输出 UTF-8 内容时编码失败

**解决**：
```bash
# PowerShell
$env:PYTHONIOENCODING="utf-8"
python skills/doubao-chat/scripts/chat.py "问题" --standalone

# CMD
chcp 65001
set PYTHONIOENCODING=utf-8
python skills/doubao-chat/scripts/chat.py "问题" --standalone
```

### 问题2：使用 `--questions-file` 时提示缺少 positional 参数

**现象**：报错 `error: the following arguments are required: questions`

**原因**：旧版本脚本要求必须有 positional 参数，即使使用了 `--questions-file`

**解决**：
```bash
# 添加占位符参数
python skills/doubao-chat/scripts/chat.py --questions-file questions.txt "placeholder" --standalone

# 或升级脚本后（已修复），直接使用
python skills/doubao-chat/scripts/chat.py --questions-file questions.txt --standalone
```

### 问题3：执行超时

**现象**：Query 发送后长时间无响应，最终报错 `RESPONSE_TIMEOUT`

**原因**：豆包回答较慢（尤其是复杂问题），默认 120 秒超时可能不足

**解决**：增大超时时间
```bash
python skills/doubao-chat/scripts/chat.py "问题" --standalone --timeout=180
```

### 问题4：批量提问时混入占位符

**现象**：结果中包含名为 `placeholder` 的问题

**原因**：使用 `--questions-file` 时误将占位符传入问题列表

**解决**：脚本已自动过滤 `placeholder`、`null`、`none` 等占位符值

## 使用说明

1. **优先使用 Standalone 模式**：`python skills/doubao-chat/scripts/chat.py "问题" --standalone`
2. 执行脚本并等待进程结束，一次性获取结果
3. 解析输出 JSON：
   - 单问题：读取 `answer` 字段，`references` 字段含引用链接
   - 多问题：读取 `results` 数组，遍历每项的 `question`/`answer`/`references`
4. **Cookie 持久化**：首次登录后自动保存到 `~/.doubao-chat/state.json`，后续调用自动加载
5. 如需多轮对话（上下文关联），不使用 `--new-thread`
6. 遇到错误时，使用 `--verbose` 和 `--screenshot-dir` 获取调试信息
7. **不要在对话中反复追问进度**，脚本会自动等待回复完成

## 调用示例

```bash
# 单问题 — 测试豆包是否推荐某手机
python skills/doubao-chat/scripts/chat.py "3000元以下有什么手机推荐？" --standalone

# 多问题批量 — 覆盖不同维度
python skills/doubao-chat/scripts/chat.py \
  "3000元以下有什么手机推荐？" \
  "小米15和iQOO 13哪个更适合打游戏？" \
  "拍照好的手机有哪些？" \
  --standalone

# 从文件读取问题（手机GEO健康检查场景）
# 1. 创建问题文件（UTF-8编码）
echo "帮我推荐一款轻薄好用的手机" > queries.txt
echo "7000元左右轻薄旗舰手机推荐" >> queries.txt
echo "iPhone 17 Air 值得买吗" >> queries.txt

# 2. Windows PowerShell 执行（处理编码）
$env:PYTHONIOENCODING="utf-8"
python skills/doubao-chat/scripts/chat.py --questions-file queries.txt --standalone --timeout=180

# 3. Windows CMD 执行
chcp 65001
set PYTHONIOENCODING=utf-8
python skills/doubao-chat/scripts/chat.py --questions-file queries.txt --standalone --timeout=180

# 4. Linux/Mac 执行
PYTHONIOENCODING=utf-8 python skills/doubao-chat/scripts/chat.py --questions-file queries.txt --standalone --timeout=180

# 开启新对话（避免上下文干扰）
python skills/doubao-chat/scripts/chat.py "小米15 Ultra值得买吗？" --standalone --new-thread

# 延长等待时间（复杂问题豆包回复较慢）
python skills/doubao-chat/scripts/chat.py "详细对比小米15、iQOO 13、一加12的续航表现" --standalone --timeout=180

# 调试模式（排查Cookie失效或DOM变化）
python skills/doubao-chat/scripts/chat.py "测试问题" --standalone --verbose --screenshot-dir=./debug
```

## 注意事项

- **Cookie 持久化**：`~/.doubao-chat/state.json` 保存了登录态，删除此文件需重新登录
- Cookie 有效期取决于豆包的 session 策略，过期后需重新登录
- 多问题在同一浏览器会话中顺序发送，共享上下文（除非使用 `--new-thread`）
- CDP 模式下 Chrome 必须以 `--remote-debugging-port=9222` 启动
- 豆包的 DOM 结构可能随版本更新变化，脚本使用多级选择器策略具备一定容错能力
- 引用提取依赖豆包回复中的 `<a>` 标签和引用标记，部分回复可能无引用
