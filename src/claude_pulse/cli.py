"""CLI 命令行界面 - Command Line Interface

主入口，提供所有命令行命令
"""
import asyncio
import json as json_lib
import sys

import click
from rich.console import Console

from . import __version__
from .config import get_config_manager
from .fetcher import UsageFetcher
from .formatter import ThirdPartyFormatter, UsageFormatter
from .thirdparty import ThirdPartyFetcher

# 全局 Console 用于错误输出
console = Console(stderr=True)


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--cdp-url",
    default="http://localhost:9222",
    help="浏览器 DevTools Protocol URL - Browser CDP URL (默认: http://localhost:9222)",
    show_default=True,
)
@click.pass_context
def app(ctx: click.Context, cdp_url: str):
    """Claude Pulse - 监控 Claude 使用量

    Monitor your Claude usage from the command line.

    支持的浏览器 Supported Browsers:
      - Microsoft Edge (推荐 Recommended)
      - Google Chrome
      - Chromium

    示例 Examples:
      claude-pulse usage show              # 查看使用量
      claude-pulse usage show --json       # JSON 格式输出
      claude-pulse usage show --no-color   # 禁用颜色
    """
    # 将全局配置存储在 context 中
    ctx.ensure_object(dict)
    ctx.obj["cdp_url"] = cdp_url


@app.group()
def usage():
    """使用量相关命令 - Usage related commands"""
    pass


@app.group()
def config():
    """配置管理命令 - Configuration management commands"""
    pass


@usage.command("show")
@click.option(
    "--source",
    type=click.Choice(["all", "claude", "pincc"], case_sensitive=False),
    default="all",
    help="数据来源：all(全部), claude(Claude官方), pincc(第三方) - Data source",
    show_default=True,
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="以 JSON 格式输出 - Output in JSON format",
)
@click.option(
    "--no-color",
    is_flag=True,
    help="禁用彩色输出 - Disable colored output",
)
@click.pass_context
def usage_show(
    ctx: click.Context, source: str, output_json: bool, no_color: bool
):
    """显示使用量 - Show usage data

    默认显示所有来源的使用量数据（Claude官方 + 第三方）
    Default shows usage from all sources (Claude official + third-party)

    前置要求 Prerequisites (仅 Claude官方):
      - Edge/Chrome 浏览器正在运行（启用远程调试）
      - 已登录 claude.ai

    示例 Examples:
      claude-pulse usage show                    # 显示所有来源
      claude-pulse usage show --source claude    # 仅显示 Claude官方
      claude-pulse usage show --source pincc     # 仅显示第三方
      claude-pulse usage show --json             # JSON 格式
    """
    cdp_url = ctx.obj["cdp_url"]
    source = source.lower()

    async def _fetch_and_display():
        """异步获取并显示数据"""
        results = {}
        errors = []

        # 根据 source 参数决定获取哪些数据
        fetch_claude = source in ["all", "claude"]
        fetch_pincc = source in ["all", "pincc"]

        # 获取 Claude 官方使用量
        if fetch_claude:
            try:
                if not output_json:
                    console.print(
                        "[cyan]正在获取 Claude 官方使用量... "
                        "Fetching Claude official usage...[/cyan]"
                    )
                fetcher = UsageFetcher(cdp_url=cdp_url)
                try:
                    usage_data = await fetcher.fetch_current()
                    results["claude"] = usage_data
                finally:
                    await fetcher.close()
            except Exception as e:
                errors.append(("claude", e))
                if source == "claude":  # 如果只获取 Claude 就直接报错退出
                    _handle_error(e, output_json)
                    sys.exit(1)

        # 获取第三方使用量
        if fetch_pincc:
            try:
                if not output_json:
                    console.print(
                        "[cyan]正在获取第三方使用量... "
                        "Fetching third-party usage...[/cyan]"
                    )
                third_party_fetcher = ThirdPartyFetcher()
                pincc_data = await third_party_fetcher.fetch_usage()
                results["pincc"] = pincc_data
            except Exception as e:
                errors.append(("pincc", e))
                if source == "pincc":  # 如果只获取 Pincc 就直接报错退出
                    _handle_error(e, output_json)
                    sys.exit(1)

        # 输出结果
        if output_json:
            # JSON 格式输出
            output_data = {}
            if "claude" in results:
                output_data["claude"] = results["claude"].model_dump(mode="json")
            if "pincc" in results:
                output_data["pincc"] = results["pincc"].model_dump(mode="json")
            if errors:
                output_data["errors"] = [
                    {"source": src, "error": str(err)} for src, err in errors
                ]
            output = json_lib.dumps(
                output_data, indent=2, ensure_ascii=False, default=str
            )
            click.echo(output)
        else:
            # 表格格式输出
            if "claude" in results:
                console.print()  # 空行
                formatter = UsageFormatter(no_color=no_color)
                formatter.format_table(results["claude"])

            if "pincc" in results:
                console.print()  # 空行
                third_party_formatter = ThirdPartyFormatter(no_color=no_color)
                third_party_formatter.format_table(results["pincc"])

            # 显示错误（如果有）
            if errors:
                console.print()  # 空行
                for src, err in errors:
                    console.print(
                        f"[yellow]⚠️  无法获取 {src} 数据: {str(err)}[/yellow]"
                    )

    # 运行异步任务
    asyncio.run(_fetch_and_display())


def _handle_error(error: Exception, json_output: bool = False) -> None:
    """处理错误并显示友好的错误消息

    Args:
        error: 异常对象
        json_output: 是否使用 JSON 格式输出错误
    """
    if json_output:
        # JSON 格式错误
        error_data = {
            "error": True,
            "message": str(error),
            "type": type(error).__name__,
        }
        click.echo(json_lib.dumps(error_data, indent=2), err=True)
    else:
        # 友好的错误消息
        console.print(f"\n[bold red]❌ 错误 Error:[/bold red] {str(error)}\n")

        # 根据错误类型提供故障排除建议
        error_msg = str(error).lower()

        console.print("[yellow]故障排除 Troubleshooting:[/yellow]")

        if "connect" in error_msg or "connection" in error_msg:
            console.print("  1. 确保浏览器正在运行（Edge 或 Chrome）")
            console.print("     Ensure browser is running (Edge or Chrome)")
            console.print("\n  启动 Edge (推荐) Launch Edge (Recommended):")
            console.print("     macOS:")
            console.print(
                '       /Applications/Microsoft\\ Edge.app/Contents/MacOS/Microsoft\\ Edge \\'
            )
            console.print("         --remote-debugging-port=9222 &")
            console.print("\n  启动 Chrome Launch Chrome:")
            console.print("     macOS:")
            console.print(
                '       /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\'
            )
            console.print("         --remote-debugging-port=9222 &")
        elif "context" in error_msg:
            console.print("  1. 确保浏览器有打开的标签页")
            console.print("     Ensure browser has open tabs")
            console.print("  2. 确保已登录 claude.ai")
            console.print("     Ensure you are logged into claude.ai")
        else:
            console.print("  1. 检查浏览器是否正在运行")
            console.print("     Check if browser is running")
            console.print("  2. 确保已登录 claude.ai")
            console.print("     Ensure you are logged into claude.ai")
            console.print("  3. 尝试使用 --cdp-url 指定自定义 CDP 地址")
            console.print("     Try using --cdp-url to specify custom CDP address")

        console.print("\n[dim]详细错误信息 Detailed error:[/dim]")
        console.print(f"[dim]{type(error).__name__}: {error}[/dim]")


@config.command("init")
def config_init():
    """初始化配置文件 - Initialize configuration file

    交互式创建配置文件，引导用户输入必要的配置项。
    Interactively create configuration file with guided setup.

    示例 Example:
      claude-pulse config init
    """
    config_manager = get_config_manager()

    # 检查是否已存在配置
    if config_manager.exists():
        console.print(
            f"\n[yellow]⚠️  配置文件已存在:[/yellow] "
            f"[cyan]{config_manager.get_config_path()}[/cyan]\n"
        )
        if not click.confirm("是否要重新配置？Overwrite existing config?", default=False):
            console.print("[dim]已取消 Cancelled[/dim]\n")
            return

    # 交互式初始化
    try:
        config_manager.init_interactive()
    except Exception as e:
        console.print(f"\n[red]❌ 配置失败 Failed:[/red] {e}\n")
        sys.exit(1)


@config.command("show")
def config_show():
    """显示当前配置 - Show current configuration

    显示配置文件的内容和路径。
    Display configuration file content and path.

    示例 Example:
      claude-pulse config show
    """
    config_manager = get_config_manager()

    if not config_manager.exists():
        console.print(
            "\n[yellow]⚠️  配置文件不存在[/yellow] "
            "[dim]Configuration file does not exist[/dim]\n"
        )
        console.print(
            "[dim]提示: 运行 [/dim][cyan]claude-pulse config init[/cyan] "
            "[dim]创建配置文件[/dim]\n"
        )
        return

    try:
        config = config_manager.load()
        config_path = config_manager.get_config_path()

        console.print(
            f"\n[bold cyan]配置文件路径 Config File:[/bold cyan] "
            f"[green]{config_path}[/green]\n"
        )

        # 显示配置内容
        console.print("[bold cyan]配置内容 Configuration:[/bold cyan]\n")

        # Pincc 配置
        console.print("[bold]Pincc API:[/bold]")
        if config.pincc.api_id:
            # 隐藏部分 API ID（安全考虑）
            masked_id = (
                config.pincc.api_id[:8] + "****" + config.pincc.api_id[-4:]
                if len(config.pincc.api_id) > 12
                else "****"
            )
            console.print(f"  API ID: [green]{masked_id}[/green]")
        else:
            console.print("  API ID: [dim]未配置 Not configured[/dim]")

        # 默认配置
        console.print("\n[bold]默认配置 Defaults:[/bold]")
        console.print(f"  输出格式 Output Format: [cyan]{config.defaults.output_format}[/cyan]")
        console.print(
            f"  禁用颜色 No Color: [cyan]{config.defaults.no_color}[/cyan]"
        )
        console.print(f"  默认数据源 Source: [cyan]{config.defaults.source}[/cyan]")

        console.print()

    except Exception as e:
        console.print(f"\n[red]❌ 读取配置失败 Failed:[/red] {e}\n")
        sys.exit(1)


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """设置配置项 - Set configuration value

    设置指定的配置项的值。
    Set the value of a configuration key.

    支持的配置项 Supported keys:
      - pincc.api_id          第三方 API ID
      - defaults.output_format  输出格式 (table, json)
      - defaults.no_color      禁用颜色 (true, false)
      - defaults.source        默认数据源 (all, claude, pincc)

    示例 Examples:
      claude-pulse config set pincc.api_id "your-api-id"
      claude-pulse config set defaults.output_format json
      claude-pulse config set defaults.source pincc
    """
    config_manager = get_config_manager()

    try:
        # 加载现有配置或创建新配置
        config = config_manager.load()

        # 解析 key (支持嵌套，如 pincc.api_id)
        parts = key.split(".")
        if len(parts) != 2:
            console.print(
                f"\n[red]❌ 无效的配置项:[/red] {key}\n"
                "[dim]格式应为: section.key (例如: pincc.api_id)[/dim]\n"
            )
            sys.exit(1)

        section, config_key = parts

        # 根据 section 更新配置
        if section == "pincc":
            if config_key == "api_id":
                config.pincc.api_id = value
            else:
                console.print(f"\n[red]❌ 未知的配置项:[/red] {key}\n")
                sys.exit(1)
        elif section == "defaults":
            if config_key == "output_format":
                if value not in ["table", "json"]:
                    console.print(
                        f"\n[red]❌ 无效的值:[/red] {value}\n"
                        "[dim]output_format 必须是 'table' 或 'json'[/dim]\n"
                    )
                    sys.exit(1)
                config.defaults.output_format = value
            elif config_key == "no_color":
                config.defaults.no_color = value.lower() in ["true", "1", "yes"]
            elif config_key == "source":
                if value not in ["all", "claude", "pincc"]:
                    console.print(
                        f"\n[red]❌ 无效的值:[/red] {value}\n"
                        "[dim]source 必须是 'all', 'claude' 或 'pincc'[/dim]\n"
                    )
                    sys.exit(1)
                config.defaults.source = value
            else:
                console.print(f"\n[red]❌ 未知的配置项:[/red] {key}\n")
                sys.exit(1)
        else:
            console.print(f"\n[red]❌ 未知的配置分组:[/red] {section}\n")
            sys.exit(1)

        # 保存配置
        config_manager.save(config)

        console.print(
            f"\n[green]✅ 配置已更新:[/green] [cyan]{key}[/cyan] = [yellow]{value}[/yellow]\n"
        )

    except Exception as e:
        console.print(f"\n[red]❌ 设置配置失败 Failed:[/red] {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    app()
