# Claude Pulse

监控 Claude 使用量的命令行工具 - Monitor Claude usage from CLI

快速查看你的 Claude API 使用量，无需打开浏览器！

## ✨ 特性 Features

- 📊 美观的终端表格显示使用量数据
- 🎨 彩色输出和进度条
- 📱 JSON 格式输出支持
- 🌐 中英文双语界面
- 🔒 复用浏览器登录态，无需额外认证
- 🌍 支持 Edge、Chrome 等 Chromium 浏览器
- ⚡ 快速原型，简单易用

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
# 查看使用量（表格格式）
claude-pulse usage show

# JSON 格式输出
claude-pulse usage show --json

# 禁用彩色输出（适用于脚本）
claude-pulse usage show --no-color

# 自定义浏览器调试端口
claude-pulse --cdp-url http://localhost:9223 usage show

# 查看帮助
claude-pulse --help
claude-pulse usage show --help
```

## 📖 示例输出 Example Output

### 表格格式 Table Format
```
Claude Usage - 2025-10

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ 指标 Metric        ┃ 已使用 / 配额       ┃ 百分比 Percentage ┃ 状态     ┃
┣━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━┫
┃ 输入 Tokens        ┃ 1,234,567 / 5,000,000 ┃ 24.7%           ┃ 🔵      ┃
┃ 输出 Tokens        ┃ 654,321 / 2,500,000   ┃ 26.2%           ┃ 🔵      ┃
┃ 总消息数           ┃ 150                   ┃ -               ┃ 📊      ┃
┗━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━┛
```

### JSON 格式 JSON Format
```json
{
  "billing_period": "2025-10",
  "period_start": "2025-10-01T00:00:00",
  "period_end": "2025-10-31T23:59:59",
  "input_tokens_used": 1234567,
  "input_tokens_quota": 5000000,
  "output_tokens_used": 654321,
  "output_tokens_quota": 2500000,
  "total_messages": 150,
  "input_usage_percent": 24.7,
  "output_usage_percent": 26.2,
  "overall_usage_percent": 25.45
}
```

## 🔧 开发 Development

### 项目结构 Project Structure
```
src/claude_pulse/
  ├── __init__.py       # 包初始化
  ├── __main__.py       # CLI 入口
  ├── cli.py            # 命令行界面
  ├── models.py         # 数据模型
  ├── browser.py        # 浏览器服务
  ├── fetcher.py        # 使用量抓取
  └── formatter.py      # 输出格式化
```

### 运行测试 Run Tests
```bash
# 代码检查
ruff check src/

# 手动测试
python -m claude_pulse usage show
```

## 🎯 原型状态 Prototype Status

当前版本：**v0.1.0** - 快速原型

✅ **已完成 Completed:**
- 核心功能：查看使用量
- 美观的终端输出
- JSON 格式支持
- 错误处理和友好提示
- 中英文双语支持

🚧 **待实现 TODO (后续版本):**
- 真实 API 数据抓取（当前使用模拟数据）
- 历史趋势追踪
- 使用量告警
- 配置文件支持
- 单元测试和集成测试

## 📝 注意事项 Notes

1. **当前版本使用模拟数据** - 实际的 Claude API 数据抓取需要根据真实 API 端点调整
2. **需要手动启动浏览器** - 确保浏览器以调试模式运行（推荐使用 Edge）
3. **原型版本** - 专注快速交付，后续会添加更多功能
4. **浏览器兼容性** - 支持所有基于 Chromium 的浏览器（Edge、Chrome、Brave 等）

## 🤝 贡献 Contributing

欢迎提交 Issue 和 Pull Request！

## 📄 许可 License

MIT License
