"""格式化器 - Formatter

使用 Rich 库将使用量数据格式化为美观的终端输出
"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import UsageData


class UsageFormatter:
    """使用量格式化器 - Usage Formatter

    将 UsageData 格式化为终端表格和图表
    """

    def __init__(self, no_color: bool = False):
        """初始化格式化器

        Args:
            no_color: 是否禁用颜色输出
        """
        self.console = Console(force_terminal=not no_color, no_color=no_color)

    def format_table(self, usage: UsageData) -> None:
        """显示使用量表格 - Display usage table

        Args:
            usage: 使用量数据
        """
        # 创建标题
        title = Text(f"Claude Usage - {usage.billing_period}", style="bold cyan")

        # 创建表格
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("指标 Metric", style="cyan", width=20)
        table.add_column("已使用 / 配额 Used / Quota", justify="right", style="yellow")
        table.add_column("百分比 Percentage", justify="right", style="green")
        table.add_column("状态 Status", justify="center", width=10)

        # 添加输入 tokens 行
        input_status = self._get_status_emoji(usage.input_usage_percent)
        table.add_row(
            "输入 Tokens\nInput Tokens",
            f"{usage.input_tokens_used:,} / {usage.input_tokens_quota:,}",
            f"{usage.input_usage_percent:.1f}%",
            input_status,
        )

        # 添加输出 tokens 行
        output_status = self._get_status_emoji(usage.output_usage_percent)
        table.add_row(
            "输出 Tokens\nOutput Tokens",
            f"{usage.output_tokens_used:,} / {usage.output_tokens_quota:,}",
            f"{usage.output_usage_percent:.1f}%",
            output_status,
        )

        # 添加总消息数行
        table.add_row(
            "总消息数\nTotal Messages",
            f"{usage.total_messages:,}",
            "-",
            "📊",
        )

        # 打印表格
        self.console.print(table)

        # 添加进度条
        self._show_progress_bars(usage)

        # 添加时间信息
        self._show_period_info(usage)

    def _get_status_emoji(self, percent: float) -> str:
        """根据使用百分比返回状态表情 - Get status emoji based on percentage

        Args:
            percent: 使用百分比

        Returns:
            str: 状态表情符号
        """
        if percent >= 90:
            return "🔴"  # 红色 - 严重
        elif percent >= 80:
            return "🟡"  # 黄色 - 警告
        elif percent >= 50:
            return "🟢"  # 绿色 - 正常
        else:
            return "🔵"  # 蓝色 - 良好

    def _show_progress_bars(self, usage: UsageData) -> None:
        """显示进度条 - Show progress bars

        Args:
            usage: 使用量数据
        """
        self.console.print("\n[bold]使用量进度 Usage Progress:[/bold]")

        # 输入 tokens 进度条
        input_bar = self._create_progress_bar(
            "Input Tokens", usage.input_usage_percent, usage.input_tokens_quota
        )
        self.console.print(input_bar)

        # 输出 tokens 进度条
        output_bar = self._create_progress_bar(
            "Output Tokens", usage.output_usage_percent, usage.output_tokens_quota
        )
        self.console.print(output_bar)

    def _create_progress_bar(self, label: str, percent: float, total: int) -> str:
        """创建进度条文本 - Create progress bar text

        Args:
            label: 标签
            percent: 百分比
            total: 总量

        Returns:
            str: 进度条文本
        """
        # 计算进度条长度（最大 40 个字符）
        bar_length = 40
        filled_length = int(bar_length * percent / 100)

        # 选择颜色
        if percent >= 90:
            color = "red"
        elif percent >= 80:
            color = "yellow"
        else:
            color = "green"

        # 创建进度条
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        return f"[{color}]{label:15s}[/{color}] [{color}]{bar}[/{color}] {percent:5.1f}%"

    def _show_period_info(self, usage: UsageData) -> None:
        """显示周期信息 - Show period info

        Args:
            usage: 使用量数据
        """
        period_text = (
            f"\n[dim]计费周期 Billing Period:[/dim] "
            f"{usage.period_start.strftime('%Y-%m-%d')} → "
            f"{usage.period_end.strftime('%Y-%m-%d')}\n"
            f"[dim]获取时间 Fetched At:[/dim] {usage.fetched_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.console.print(period_text)

        # 如果是高使用量，显示警告
        if usage.is_high_usage:
            warning = Panel(
                "[bold red]⚠️  警告 WARNING[/bold red]\n"
                "使用量已超过 80%，请注意控制使用\n"
                "Usage exceeds 80%, please monitor carefully",
                border_style="red",
            )
            self.console.print(warning)
