# TOOLS.md

本 workspace 无外部工具依赖，所有能力由 `skills/` 目录下的 skill 提供。

| Skill | 路径 | 用途 |
|-------|------|------|
| phone-geo-health | `skills/phone-geo-health/SKILL.md` | 手机GEO健康检查主流程（5步） |
| doubao-chat | `skills/doubao-chat/SKILL.md` | 豆包网页对话自动化（Playwright） |

## 依赖说明

- **Python 3.10+**：`python` 命令可用
- **Playwright**：`pip install playwright && playwright install chromium`
- **Cookie 持久化**：`~/.doubao-chat/state.json`（首次需手动登录豆包）
