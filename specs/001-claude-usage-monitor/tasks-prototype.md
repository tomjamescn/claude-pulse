# Tasks: Claude Usage Monitor - 快速原型版

**目标**: 1天内实现可用原型
**范围**: 核心功能 - 查看 Claude 使用量
**策略**: 先能用，再完善

---

## 快速实施路线图

### 🌅 上午 (3-4小时) - 基础设施

**Phase 1: 最小项目结构**

- [ ] T001 创建项目结构 (src/claude_pulse/, pyproject.toml)
- [ ] T002 安装核心依赖 (click, rich, pydantic, playwright)
- [ ] T003 创建 __init__.py 和 __main__.py 入口文件

**Phase 2: 核心数据模型**

- [ ] T004 创建 UsageData 模型在 src/claude_pulse/models.py (Pydantic, 包含所有字段和计算属性)

**Phase 3: MCP 浏览器连接**

- [ ] T005 实现浏览器服务 src/claude_pulse/browser.py (连接 Playwright MCP, 获取 browser context)
- [ ] T006 实现使用量抓取 src/claude_pulse/fetcher.py (导航到 claude.ai/settings/usage, 等待 API 请求, 解析响应)

---

### 🌆 下午 (3-4小时) - 用户界面

**Phase 4: 显示和 CLI**

- [ ] T007 实现 Rich 表格格式化 src/claude_pulse/formatter.py (彩色表格, 进度条)
- [ ] T008 创建 CLI 主入口 src/claude_pulse/cli.py (Click app, usage show 命令)
- [ ] T009 集成所有组件 (fetcher → formatter → CLI 输出)

**Phase 5: 基本错误处理**

- [ ] T010 添加基本错误处理 (网络错误, MCP 连接失败, 未登录检测)
- [ ] T011 添加 --json 和 --no-color 参数支持

---

### 🌙 验收测试

**Phase 6: 验证和打包**

- [ ] T012 手动测试完整流程 (MCP 连接 → 抓取 → 显示)
- [ ] T013 配置 Poetry 入口点 (claude-pulse 命令)
- [ ] T014 创建简单 README.md (安装和使用说明)

---

## 任务详情

### T001: 创建项目结构

```bash
mkdir -p src/claude_pulse
touch src/claude_pulse/__init__.py
touch src/claude_pulse/__main__.py
touch pyproject.toml
```

**pyproject.toml 基本内容**:
```toml
[tool.poetry]
name = "claude-pulse"
version = "0.1.0"
description = "Monitor Claude usage from CLI"

[tool.poetry.dependencies]
python = "^3.11"
click = "^8.1.7"
rich = "^13.7.0"
pydantic = "^2.5.0"
playwright = "^1.40.0"

[tool.poetry.scripts]
claude-pulse = "claude_pulse.cli:app"
```

---

### T002: 安装核心依赖

```bash
poetry install
```

---

### T003: 创建入口文件

**src/claude_pulse/__init__.py**:
```python
"""Claude Usage Monitor"""
__version__ = "0.1.0"
```

**src/claude_pulse/__main__.py**:
```python
from claude_pulse.cli import app

if __name__ == "__main__":
    app()
```

---

### T004: 创建 UsageData 模型

**src/claude_pulse/models.py**:
```python
from datetime import datetime
from pydantic import BaseModel, Field, computed_field

class UsageData(BaseModel):
    """Claude 使用量数据"""
    billing_period: str
    period_start: datetime
    period_end: datetime
    input_tokens_used: int
    input_tokens_quota: int
    output_tokens_used: int
    output_tokens_quota: int
    total_messages: int
    fetched_at: datetime

    @computed_field
    @property
    def input_usage_percent(self) -> float:
        return (self.input_tokens_used / self.input_tokens_quota) * 100

    @computed_field
    @property
    def output_usage_percent(self) -> float:
        return (self.output_tokens_used / self.output_tokens_quota) * 100

    @computed_field
    @property
    def overall_usage_percent(self) -> float:
        return (self.input_usage_percent + self.output_usage_percent) / 2
```

---

### T005: 实现浏览器服务

**src/claude_pulse/browser.py**:
```python
from playwright.async_api import async_playwright

class MCPBrowserService:
    """连接 Playwright MCP 扩展"""

    async def connect(self):
        """连接到 MCP 服务器"""
        # TODO: 实现 MCP 连接逻辑
        # 参考: contracts/mcp-protocol.md
        pass

    async def get_context(self):
        """获取浏览器上下文（复用现有会话）"""
        playwright = await async_playwright().start()
        # 连接到已运行的 Chrome (通过 MCP)
        browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]  # 使用现有上下文
        return context
```

---

### T006: 实现使用量抓取

**src/claude_pulse/fetcher.py**:
```python
import asyncio
from datetime import datetime
from .browser import MCPBrowserService
from .models import UsageData

class UsageFetcher:
    """从 Claude 网站抓取使用量"""

    def __init__(self):
        self.browser_service = MCPBrowserService()

    async def fetch_current(self) -> UsageData:
        """获取当前使用量"""
        context = await self.browser_service.get_context()
        page = await context.new_page()

        # 导航到使用量页面
        await page.goto("https://claude.ai/settings/usage")

        # 等待 API 请求完成 (需要通过 DevTools 确认实际端点)
        # 简化版: 直接等待页面加载
        await page.wait_for_load_state("networkidle")

        # 从页面提取数据 (需要实际调试确定选择器)
        # 临时方案: 拦截网络请求
        usage_data_raw = await page.evaluate("""
            // 这里需要根据实际页面结构提取数据
            // 或者拦截 XHR 请求
        """)

        # 解析为 UsageData
        return UsageData(
            billing_period="2025-10",
            period_start=datetime.now(),
            period_end=datetime.now(),
            input_tokens_used=1000000,
            input_tokens_quota=5000000,
            output_tokens_used=500000,
            output_tokens_quota=2500000,
            total_messages=100,
            fetched_at=datetime.now()
        )
```

---

### T007: 实现 Rich 表格格式化

**src/claude_pulse/formatter.py**:
```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from .models import UsageData

class UsageFormatter:
    """格式化使用量数据为终端表格"""

    def __init__(self, no_color: bool = False):
        self.console = Console(force_terminal=not no_color)

    def format_table(self, usage: UsageData) -> None:
        """显示使用量表格"""
        table = Table(title=f"Claude Usage - {usage.billing_period}")

        table.add_column("Metric", style="cyan")
        table.add_column("Used / Quota", style="magenta")
        table.add_column("Percentage", style="green")

        # Input tokens
        table.add_row(
            "Input Tokens",
            f"{usage.input_tokens_used:,} / {usage.input_tokens_quota:,}",
            f"{usage.input_usage_percent:.1f}%"
        )

        # Output tokens
        table.add_row(
            "Output Tokens",
            f"{usage.output_tokens_used:,} / {usage.output_tokens_quota:,}",
            f"{usage.output_usage_percent:.1f}%"
        )

        # Messages
        table.add_row(
            "Total Messages",
            f"{usage.total_messages:,}",
            "-"
        )

        self.console.print(table)
```

---

### T008: 创建 CLI 主入口

**src/claude_pulse/cli.py**:
```python
import click
import asyncio
from .fetcher import UsageFetcher
from .formatter import UsageFormatter

@click.group()
@click.version_option(version="0.1.0")
def app():
    """Claude Usage Monitor - 查看 Claude 使用量"""
    pass

@app.command()
@click.option("--json", is_flag=True, help="JSON 格式输出")
@click.option("--no-color", is_flag=True, help="禁用彩色输出")
def usage_show(json: bool, no_color: bool):
    """显示当前使用量"""
    async def _fetch_and_display():
        fetcher = UsageFetcher()
        usage = await fetcher.fetch_current()

        if json:
            import json as json_lib
            click.echo(json_lib.dumps(usage.model_dump(), default=str, indent=2))
        else:
            formatter = UsageFormatter(no_color=no_color)
            formatter.format_table(usage)

    asyncio.run(_fetch_and_display())

if __name__ == "__main__":
    app()
```

---

### T009: 集成所有组件

在 T008 中已完成，无需额外文件。

---

### T010: 添加基本错误处理

**更新 src/claude_pulse/fetcher.py**:
```python
class UsageFetcher:
    async def fetch_current(self) -> UsageData:
        try:
            context = await self.browser_service.get_context()
            # ... 现有逻辑
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)
            click.echo("\nTroubleshooting:")
            click.echo("1. Ensure Chrome is running")
            click.echo("2. Ensure Playwright MCP extension is installed")
            click.echo("3. Ensure you're logged into claude.ai")
            raise
```

---

### T011: 添加参数支持

已在 T008 中实现 (--json, --no-color)。

---

### T012: 手动测试

```bash
# 安装依赖
poetry install

# 运行测试
poetry run claude-pulse usage-show

# 测试 JSON 输出
poetry run claude-pulse usage-show --json

# 测试无颜色
poetry run claude-pulse usage-show --no-color
```

---

### T013: 配置入口点

已在 T001 的 pyproject.toml 中配置。

安装后可直接使用:
```bash
poetry install
claude-pulse usage-show
```

---

### T014: 创建 README

**README.md**:
```markdown
# Claude Pulse

监控 Claude 使用量的命令行工具。

## 安装

```bash
pip install claude-pulse
```

## 使用

```bash
# 查看使用量
claude-pulse usage-show

# JSON 格式
claude-pulse usage-show --json

# 纯文本（无颜色）
claude-pulse usage-show --no-color
```

## 前置要求

1. Chrome 浏览器
2. Playwright MCP 扩展已安装
3. 已登录 claude.ai
```

---

## 快速启动

```bash
# 1. 克隆/创建项目
cd claude-pulse

# 2. 按顺序执行 T001-T014
# 建议分组执行:

# 上午: T001-T006 (基础 + 数据抓取)
# 下午: T007-T011 (UI + CLI)
# 晚上: T012-T014 (测试 + 打包)

# 3. 第一次运行
poetry run claude-pulse usage-show
```

---

## 总结

**任务数**: 14 个（精简版 vs 原 85 个）
**预计时间**: 6-8 小时（1 个工作日）
**核心功能**:
- ✅ 查看当前 Claude 使用量
- ✅ 美观的表格显示
- ✅ JSON 输出支持

**后续改进**（可选）:
- 添加测试
- 历史追踪
- 配置管理
- 告警功能

**立即开始**: 从 T001 开始执行！🚀
