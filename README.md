# Claude Pulse

监控 Claude 使用量的命令行工具 - Monitor Claude usage from CLI

快速查看你的 Claude 使用量，支持官方和第三方 API，无需打开浏览器！

## ✨ 特性 Features

- 🎯 **双数据源支持**
  - Claude 官方使用量（claude.ai）
  - 第三方 API 使用量（pincc.ai）
  - 可选择单独或同时查看
- 📊 **美观的终端表格显示**
  - 彩色输出和进度条
  - 使用率可视化
  - 时间窗口限制展示
- 📱 **多种输出格式**
  - 友好的表格格式（默认）
  - JSON 格式（适用于脚本集成）
  - 纯文本模式（--no-color）
- 🌐 **中英文双语界面**
- 🔒 **安全便捷**
  - 复用浏览器登录态，无需额外认证
  - 支持 Edge、Chrome 等 Chromium 浏览器
- ⚡ **快速高效**
  - 异步并发获取数据
  - 友好的错误提示

## 🚀 快速开始 Quick Start

### 安装 Installation

```bash
# 从源码安装（开发版本）
git clone <repository-url>
cd claude-pulse
uv venv  # 或 python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### 前置要求 Prerequisites

1. **Edge 或 Chrome 浏览器** - 启用远程调试

   **Microsoft Edge (推荐 Recommended):**
   ```bash
   # macOS
   /Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --remote-debugging-port=9222 &

   # Windows
   "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222

   # Linux
   microsoft-edge --remote-debugging-port=9222 &
   ```

   **Google Chrome:**
   ```bash
   # macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &

   # Windows
   chrome.exe --remote-debugging-port=9222

   # Linux
   google-chrome --remote-debugging-port=9222 &
   ```

2. **登录 claude.ai**
   - 在浏览器中登录 https://claude.ai

### 使用 Usage

```bash
# 查看所有来源的使用量（默认：Claude官方 + 第三方）
claude-pulse usage show

# 仅查看 Claude 官方使用量
claude-pulse usage show --source claude

# 仅查看第三方 API 使用量（无需浏览器）
claude-pulse usage show --source pincc

# JSON 格式输出
claude-pulse usage show --json

# 禁用彩色输出（适用于脚本）
claude-pulse usage show --no-color

# 自定义浏览器调试端口（仅影响 Claude 官方数据获取）
claude-pulse --cdp-url http://localhost:9223 usage show

# 查看帮助
claude-pulse --help
claude-pulse usage show --help
```

## 🎨 命令行参数 CLI Options

### 全局参数

```bash
--cdp-url TEXT          # 浏览器 CDP URL (默认: http://localhost:9222)
--version               # 显示版本信息
--help                  # 显示帮助信息
```

### usage show 命令参数

```bash
--source [all|claude|pincc]   # 数据来源 (默认: all)
                               # all    - 显示所有来源
                               # claude - 仅显示 Claude 官方
                               # pincc  - 仅显示第三方 API

--json                        # 以 JSON 格式输出

--no-color                    # 禁用彩色输出（适用于脚本/日志）
```

### 使用示例

```bash
# 查看所有数据源
claude-pulse usage show

# 仅查看 Claude 官方（需要浏览器）
claude-pulse usage show --source claude

# 仅查看第三方 API（无需浏览器，最快）
claude-pulse usage show --source pincc

# JSON 格式输出（适合脚本集成）
claude-pulse usage show --json

# 纯文本输出（无颜色）
claude-pulse usage show --no-color

# 自定义浏览器端口
claude-pulse --cdp-url http://localhost:9223 usage show --source claude
```

## 📖 示例输出 Example Output

### 表格格式 Table Format

#### Claude 官方使用量
```
       Claude Usage - Plan usage limits
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ 项目 Item                  ┃ 值 Value         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 会话类型                   │ Current session  │
│ Session Type               │                  │
│ 使用率                     │ 14% used 🔵      │
│ Usage                      │                  │
│ 重置时间                   │ 2 hr 19 min      │
│ Resets In                  │                  │
│ 最后更新                   │ just now         │
│ Last Updated               │                  │
└───────────────────────────┴─────────────────┘

使用量进度 Usage Progress:
Usage          ███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  14.0%
```

#### 第三方 API 使用量
```
                  Third-party Claude API Usage
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃                           ┃     已使用 ┃            ┃      剩余 ┃    状态    ┃
┃ 限制类型 Limit Type        ┃       Used ┃ 限制 Limit ┃ Remaining ┃   Status   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ ⏱️  时间窗口限制           │   $77.3853 │  $133.0000 │  $55.6147 │      🟢    │
│ Time Window Limit         │            │            │           │            │
└───────────────────────────┴────────────┴────────────┴───────────┴────────────┘

时间窗口 Time Window: 剩余 5 小时 52 分钟 (Remaining 5h 52m)
窗口时间 Window Period: 2025-10-26 12:32 → 2025-11-02 12:32

总费用 Total Cost: $210.5427
```

### JSON 格式 JSON Format
```json
{
  "claude": {
    "session_type": "Current session",
    "reset_minutes": 139,
    "usage_percent": 14.0,
    "fetched_at": "2025-11-02T06:40:40"
  },
  "pincc": {
    "api_id": "719b5189-1855-4982-9331-a15927e34525",
    "time_window_limit": {
      "type": "Time Window Limit",
      "value": 133.0,
      "used": 77.3853,
      "remaining": 55.6147,
      "unit": "USD"
    },
    "window_start_time": "2025-10-26T12:32:00",
    "window_end_time": "2025-11-02T12:32:00",
    "window_remaining_seconds": 21120,
    "total_cost": 210.5427,
    "fetched_at": "2025-11-02T06:40:41"
  }
}
```

## 🔧 开发 Development

### 项目结构 Project Structure
```
src/claude_pulse/
  ├── __init__.py       # 包初始化
  ├── __main__.py       # CLI 入口
  ├── cli.py            # 命令行界面 (Click)
  ├── models.py         # 数据模型 (Pydantic)
  ├── browser.py        # 浏览器服务 (Playwright CDP)
  ├── fetcher.py        # Claude 官方使用量抓取
  ├── thirdparty.py     # 第三方 API 使用量抓取
  └── formatter.py      # 输出格式化 (Rich)
```

### 运行测试 Run Tests
```bash
# 代码检查
ruff check src/

# 手动测试
python -m claude_pulse usage show
```

## 🎯 项目状态 Project Status

当前版本：**v0.1.0**

✅ **已完成 Completed:**
- ✅ Claude 官方使用量监控
  - 通过 Playwright CDP 连接浏览器
  - 从 claude.ai/settings/usage 页面抓取数据
  - 支持会话类型和重置时间显示
- ✅ 第三方 API 使用量监控
  - 直接调用 pincc.ai API
  - 显示费用限制（每日/总计/时间窗口）
  - 时间窗口剩余时间展示
  - 窗口时间范围显示
- ✅ 双数据源支持
  - 可单独或同时查看两种数据源
  - 异步并发获取，提升性能
- ✅ 美观的终端输出
  - Rich 表格格式化
  - 彩色输出和进度条
  - 使用率可视化（emoji 状态指示）
- ✅ 多种输出格式
  - 表格格式（默认）
  - JSON 格式（适合脚本集成）
  - 无颜色模式
- ✅ 错误处理和友好提示
- ✅ 中英文双语支持

🚧 **待实现 Roadmap (后续版本):**
- 历史趋势追踪和数据存储
- 使用量告警（达到阈值时通知）
- 配置文件支持（保存 API ID 等）
- 单元测试和集成测试
- 更多第三方 API 支持
- 使用量预测和建议

## 📝 注意事项 Notes

### 数据源说明

1. **Claude 官方数据** (--source claude)
   - 需要启动浏览器并开启远程调试（CDP）
   - 需要在浏览器中登录 claude.ai
   - 通过 Playwright CDP 协议连接浏览器
   - 从 claude.ai/settings/usage 页面抓取实时数据

2. **第三方 API 数据** (--source pincc)
   - 无需浏览器，直接调用 API
   - 当前使用硬编码的 API ID
   - 支持时间窗口限制展示
   - 显示详细的费用统计

### 技术说明

- **浏览器兼容性** - 支持所有基于 Chromium 的浏览器（Edge、Chrome、Brave 等）
- **异步架构** - 使用 asyncio 并发获取数据，提升性能
- **错误处理** - 单个数据源失败不影响其他数据源
- **数据实时性** - 每次运行都会获取最新数据，不做缓存

## 🤝 贡献 Contributing

欢迎提交 Issue 和 Pull Request！

## 📄 许可 License

MIT License
