# Quick Start: Claude Usage Monitor

**Target Audience**: Developers and End Users
**Estimated Time**: 5-10 minutes
**Prerequisites**: Python 3.11+, Chrome Browser

---

## 快速开始 (中文)

### 安装

```bash
# 从 PyPI 安装
pip install claude-pulse

# 验证安装
claude-pulse --version
```

### 初始设置

1. **安装 Playwright MCP Chrome 扩展**:
   ```bash
   # 克隆仓库
   git clone https://github.com/microsoft/playwright-mcp
   cd playwright-mcp/extension

   # 在 Chrome 中加载:
   # 1. 打开 chrome://extensions/
   # 2. 启用"开发者模式"
   # 3. 点击"加载已解压的扩展程序"
   # 4. 选择 'extension' 文件夹
   ```

2. **登录 Claude**:
   ```bash
   # 在 Chrome 中访问并登录
   # https://claude.ai
   ```

3. **验证连接**:
   ```bash
   claude-pulse auth check
   ```

   期望输出:
   ```
   ✓ MCP server reachable at http://localhost:3000
   ✓ Browser context available
   ✓ Claude session active
   ✓ Ready to fetch usage data
   ```

### 基本使用

**查看当前使用量**:
```bash
claude-pulse usage show
```

输出示例:
```
╔═══════════════════════════════════════════╗
║  Claude Usage - October 2025              ║
╠═══════════════════════════════════════════╣
║ Input Tokens:   1,500,000 / 5,000,000    ║
║ Progress: ██████░░░░░░░░░░  30%           ║
║                                           ║
║ Output Tokens:    750,000 / 2,500,000    ║
║ Progress: ██████░░░░░░░░░░  30%           ║
║                                           ║
║ Total Messages: 320                       ║
║                                           ║
║ Period: Oct 1 - Oct 31                    ║
║ Resets in: 12 days                        ║
╚═══════════════════════════════════════════╝
```

**JSON 格式输出** (用于脚本):
```bash
claude-pulse usage show --json
```

**纯文本输出** (无颜色):
```bash
claude-pulse usage show --no-color
```

### 帮助

```bash
# 查看所有命令
claude-pulse --help

# 查看特定命令帮助
claude-pulse usage --help
claude-pulse auth --help
```

---

## Quick Start (English)

### Installation

```bash
# Install from PyPI
pip install claude-pulse

# Verify installation
claude-pulse --version
```

### Initial Setup

1. **Install Playwright MCP Chrome Extension**:
   ```bash
   # Clone repository
   git clone https://github.com/microsoft/playwright-mcp
   cd playwright-mcp/extension

   # Load in Chrome:
   # 1. Open chrome://extensions/
   # 2. Enable "Developer mode"
   # 3. Click "Load unpacked"
   # 4. Select 'extension' folder
   ```

2. **Log into Claude**:
   ```bash
   # Visit and log in via Chrome
   # https://claude.ai
   ```

3. **Verify Connection**:
   ```bash
   claude-pulse auth check
   ```

   Expected output:
   ```
   ✓ MCP server reachable at http://localhost:3000
   ✓ Browser context available
   ✓ Claude session active
   ✓ Ready to fetch usage data
   ```

### Basic Usage

**View Current Usage**:
```bash
claude-pulse usage show
```

Output example:
```
╔═══════════════════════════════════════════╗
║  Claude Usage - October 2025              ║
╠═══════════════════════════════════════════╣
║ Input Tokens:   1,500,000 / 5,000,000    ║
║ Progress: ██████░░░░░░░░░░  30%           ║
║                                           ║
║ Output Tokens:    750,000 / 2,500,000    ║
║ Progress: ██████░░░░░░░░░░  30%           ║
║                                           ║
║ Total Messages: 320                       ║
║                                           ║
║ Period: Oct 1 - Oct 31                    ║
║ Resets in: 12 days                        ║
╚═══════════════════════════════════════════╝
```

**JSON Output** (for scripts):
```bash
claude-pulse usage show --json
```

**Plain Text Output** (no color):
```bash
claude-pulse usage show --no-color
```

### Help

```bash
# View all commands
claude-pulse --help

# View specific command help
claude-pulse usage --help
claude-pulse auth --help
```

---

## Command Reference

### Authentication Commands

```bash
# Check MCP connection and Claude session
claude-pulse auth check

# View connection status
claude-pulse auth status

# Test browser automation
claude-pulse auth test
```

### Usage Commands

```bash
# View current usage (default: table format)
claude-pulse usage show

# JSON format (for scripting)
claude-pulse usage show --json

# Plain text (no colors)
claude-pulse usage show --no-color

# Refresh and display
claude-pulse usage show --refresh
```

### Configuration Commands

```bash
# Show configuration file location
claude-pulse config show

# Edit configuration
claude-pulse config edit

# Reset to defaults
claude-pulse config reset

# Set specific option
claude-pulse config set general.color_enabled true
claude-pulse config set alerts.warning_threshold 85
```

---

## Advanced Usage

### Historical Tracking (P2 Feature)

```bash
# Save current usage as snapshot
claude-pulse history snapshot

# View history for last 7 days
claude-pulse history show --days 7

# View history for date range
claude-pulse history show --from 2025-10-01 --to 2025-10-15

# Chart view (terminal-based)
claude-pulse history chart --days 30
```

### Alerts (P3 Feature)

```bash
# Enable alerts
claude-pulse config set alerts.enabled true

# Set warning threshold (80%)
claude-pulse config set alerts.warning_threshold 80

# Set critical threshold (95%)
claude-pulse config set alerts.critical_threshold 95

# Test alert
claude-pulse alerts test
```

---

## Troubleshooting

### Error: MCP server not reachable

```
❌ Error: Could not connect to MCP server at http://localhost:3000

Possible causes:
  • Playwright MCP extension not installed
  • Extension is disabled
  • Chrome is not running

To fix:
  1. Install extension: https://github.com/microsoft/playwright-mcp
  2. Open Chrome and enable extension at chrome://extensions/
  3. Run: claude-pulse auth check
```

**Solution**:
1. Verify Chrome is running
2. Check extension is installed and enabled
3. Restart Chrome if needed

### Error: Not logged into Claude

```
❌ Error: Not logged into Claude

To fix:
  1. Open Chrome and visit: https://claude.ai
  2. Log in with your credentials
  3. Return to terminal and run: claude-pulse usage show
```

**Solution**:
1. Log into https://claude.ai in Chrome
2. Keep browser open while using `claude-pulse`

### Error: API structure changed

```
❌ Error: Claude API structure changed

The Claude API response format has changed.
This tool needs to be updated.

Please report this issue:
  https://github.com/tomjamescn/claude-pulse/issues

For detailed logs:
  ~/.local/state/claude-pulse/app.log
```

**Solution**:
1. Check for tool updates: `pip install --upgrade claude-pulse`
2. Report issue on GitHub if persists

---

## Configuration File

**Location**:
- Linux: `~/.config/claude-pulse/config.toml`
- macOS: `~/Library/Application Support/claude-pulse/config.toml`
- Windows: `%APPDATA%\claude-pulse\config.toml`

**Example**:
```toml
[general]
default_output_format = "table"  # Options: table, json, plain
color_enabled = true
log_level = "INFO"  # DEBUG, INFO, WARNING, ERROR

[alerts]
enabled = false
warning_threshold = 80
critical_threshold = 95
notify_system = false
notify_on_reset = true

[history]
retention_days = 30
auto_snapshot = false

[mcp]
mcp_server_url = "http://localhost:3000"
connection_timeout = 10
```

---

## Data Storage

**Configuration**: `~/.config/claude-pulse/`
**Usage History**: `~/.local/share/claude-pulse/usage.db` (SQLite)
**Logs**: `~/.local/state/claude-pulse/app.log`

(Paths adjusted for platform: macOS, Windows use appropriate directories)

---

## Next Steps

1. **Explore Commands**: Run `claude-pulse --help` to see all available commands
2. **Customize Config**: Edit `~/.config/claude-pulse/config.toml`
3. **Set Up Alerts**: Configure usage thresholds
4. **Historical Tracking**: Enable auto-snapshots for trend analysis

---

## Getting Help

- **Documentation**: https://github.com/tomjamescn/claude-pulse/blob/main/README.md
- **Issues**: https://github.com/tomjamescn/claude-pulse/issues
- **Discussions**: https://github.com/tomjamescn/claude-pulse/discussions

---

## License & Credits

- **License**: MIT
- **Powered by**:
  - [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
  - [Playwright MCP](https://github.com/microsoft/playwright-mcp)
  - [Rich](https://github.com/Textualize/rich)
  - [Click](https://click.palletsprojects.com/)

