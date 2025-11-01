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
        title = Text(f"Claude Usage - {usage.plan_type}", style="bold cyan")

        # 创建表格
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("项目 Item", style="cyan", width=25)
        table.add_column("值 Value", justify="left", style="yellow")

        # 添加会话类型
        table.add_row("会话类型\nSession Type", usage.session_type)

        # 添加使用百分比
        status_emoji = self._get_status_emoji(usage.usage_percent)
        table.add_row(
            "使用率\nUsage",
            f"{usage.usage_percent:.0f}% used {status_emoji}",
        )

        # 添加重置时间
        table.add_row("重置时间\nResets In", usage.reset_time)

        # 添加最后更新时间
        table.add_row("最后更新\nLast Updated", usage.last_updated)

        # 打印表格
        self.console.print(table)

        # 添加进度条
        self._show_progress_bar(usage)

        # 添加警告信息
        self._show_warning(usage)

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

    def _show_progress_bar(self, usage: UsageData) -> None:
        """显示进度条 - Show progress bar

        Args:
            usage: 使用量数据
        """
        self.console.print("\n[bold]使用量进度 Usage Progress:[/bold]")

        # 使用百分比进度条
        bar = self._create_progress_bar("Usage", usage.usage_percent)
        self.console.print(bar)

    def _create_progress_bar(self, label: str, percent: float) -> str:
        """创建进度条文本 - Create progress bar text

        Args:
            label: 标签
            percent: 百分比

        Returns:
            str: 进度条文本
        """
        # 计算进度条长度（最大 50 个字符）
        bar_length = 50
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

    def _show_warning(self, usage: UsageData) -> None:
        """显示警告信息 - Show warning

        Args:
            usage: 使用量数据
        """
        # 显示获取时间
        fetch_time = usage.fetched_at.strftime("%Y-%m-%d %H:%M:%S")
        self.console.print(
            f"\n[dim]数据获取时间 Fetched At:[/dim] {fetch_time}"
        )

        # 如果是高使用量，显示警告
        if usage.usage_percent >= 80:
            warning = Panel(
                "[bold red]⚠️  警告 WARNING[/bold red]\n"
                f"使用量已达到 {usage.usage_percent:.0f}%，请注意控制使用\n"
                f"Usage has reached {usage.usage_percent:.0f}%, please monitor carefully",
                border_style="red",
            )
            self.console.print(warning)
