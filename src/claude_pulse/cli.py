"""CLI 命令行界面 - Command Line Interface

主入口，提供所有命令行命令
"""
import asyncio
import json as json_lib
import sys

import click
from rich.console import Console

from . import __version__
from .fetcher import UsageFetcher
from .formatter import UsageFormatter

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


@usage.command("show")
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
def usage_show(ctx: click.Context, output_json: bool, no_color: bool):
    """显示当前使用量 - Show current usage

    连接到浏览器，访问 claude.ai/settings/usage 并显示使用量数据。

    前置要求 Prerequisites:
      - Edge/Chrome 浏览器正在运行（启用远程调试）
      - 已登录 claude.ai

    启动浏览器 Start Browser:
      Edge (推荐):
        macOS: /Applications/Microsoft\\ Edge.app/.../Microsoft\\ Edge
               --remote-debugging-port=9222
        Windows: msedge.exe --remote-debugging-port=9222

      Chrome:
        macOS: /Applications/Google\\ Chrome.app/.../Google\\ Chrome
               --remote-debugging-port=9222
        Windows: chrome.exe --remote-debugging-port=9222

    示例 Examples:
      claude-pulse usage show
      claude-pulse usage show --json
      claude-pulse usage show --no-color
    """
    cdp_url = ctx.obj["cdp_url"]

    async def _fetch_and_display():
        """异步获取并显示数据"""
        fetcher = UsageFetcher(cdp_url=cdp_url)

        try:
            # 显示加载提示（仅在非 JSON 模式）
            if not output_json:
                console.print("[cyan]正在连接浏览器... Connecting to browser...[/cyan]")

            # 获取使用量数据
            usage_data = await fetcher.fetch_current()

            # 输出结果
            if output_json:
                # JSON 格式输出
                output = json_lib.dumps(
                    usage_data.model_dump(mode="json"),
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )
                click.echo(output)
            else:
                # 表格格式输出
                formatter = UsageFormatter(no_color=no_color)
                formatter.format_table(usage_data)

        except Exception as e:
            # 错误处理
            _handle_error(e, output_json)
            sys.exit(1)

        finally:
            # 清理资源
            await fetcher.close()

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


if __name__ == "__main__":
    app()
