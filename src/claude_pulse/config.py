"""配置管理模块 - Configuration Management

处理配置文件的读写和管理
Handles configuration file reading and writing
"""
from pathlib import Path
from typing import Optional

try:
    import tomli
    import tomli_w
except ImportError:
    import tomllib as tomli  # Python 3.11+
    import tomli_w

from pydantic import BaseModel, Field


class PinccConfig(BaseModel):
    """Pincc 第三方 API 配置"""

    api_id: Optional[str] = Field(None, description="Pincc API ID")


class DefaultsConfig(BaseModel):
    """默认配置"""

    output_format: str = Field("table", description="输出格式: table, json")
    no_color: bool = Field(False, description="是否禁用颜色")
    source: str = Field("all", description="默认数据源: all, claude, pincc")


class Config(BaseModel):
    """完整配置"""

    pincc: PinccConfig = Field(default_factory=PinccConfig)
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)


class ConfigManager:
    """配置管理器 - Configuration Manager"""

    # 配置文件路径（优先使用 XDG 标准）
    CONFIG_DIR = Path.home() / ".config" / "claude-pulse"
    CONFIG_FILE = CONFIG_DIR / "config.toml"

    # 备用路径（兼容性）
    FALLBACK_CONFIG_FILE = Path.home() / ".claude-pulse.toml"

    def __init__(self):
        """初始化配置管理器"""
        self.config: Optional[Config] = None

    def get_config_path(self) -> Path:
        """获取配置文件路径

        Returns:
            配置文件路径
        """
        # 优先使用 XDG 标准路径
        if self.CONFIG_FILE.exists():
            return self.CONFIG_FILE

        # 备用路径
        if self.FALLBACK_CONFIG_FILE.exists():
            return self.FALLBACK_CONFIG_FILE

        # 默认返回标准路径（用于创建新配置）
        return self.CONFIG_FILE

    def load(self) -> Config:
        """加载配置文件

        Returns:
            配置对象
        """
        config_path = self.get_config_path()

        if not config_path.exists():
            # 配置文件不存在，返回默认配置
            self.config = Config()
            return self.config

        try:
            with open(config_path, "rb") as f:
                data = tomli.load(f)
                self.config = Config(**data)
                return self.config
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {config_path}: {e}")

    def save(self, config: Config) -> None:
        """保存配置到文件

        Args:
            config: 配置对象
        """
        config_path = self.get_config_path()

        # 确保配置目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 转换为字典并写入 TOML
            data = config.model_dump(mode="json")
            with open(config_path, "wb") as f:
                tomli_w.dump(data, f)
            self.config = config
        except Exception as e:
            raise RuntimeError(f"Failed to save config to {config_path}: {e}")

    def get(self) -> Config:
        """获取当前配置（缓存）

        Returns:
            配置对象
        """
        if self.config is None:
            self.config = self.load()
        return self.config

    def exists(self) -> bool:
        """检查配置文件是否存在

        Returns:
            是否存在配置文件
        """
        return self.get_config_path().exists()

    def init_interactive(self) -> Config:
        """交互式初始化配置

        Returns:
            配置对象
        """
        from rich.console import Console
        from rich.prompt import Prompt

        console = Console()

        console.print(
            "\n[bold cyan]欢迎使用 Claude Pulse！[/bold cyan] "
            "[dim]Welcome to Claude Pulse![/dim]\n"
        )
        console.print(
            "[yellow]首次使用需要配置第三方 API ID[/yellow] "
            "[dim]First-time setup: Configure third-party API ID[/dim]\n"
        )

        # 获取 Pincc API ID
        console.print(
            "[bold]请输入你的 Pincc API ID:[/bold] "
            "[dim]Enter your Pincc API ID[/dim]"
        )
        console.print("[dim]获取方式: 访问 https://pincc.ai 并登录[/dim]")
        console.print(
            "[dim]示例: 719b5189-1855-4982-9331-a15927e34525[/dim]\n",
            style="dim",
        )

        api_id = Prompt.ask("API ID", default="")

        if not api_id:
            console.print(
                "[yellow]⚠️  未输入 API ID，将跳过配置[/yellow] "
                "[dim]Skipping configuration[/dim]\n"
            )
            return Config()

        # 创建配置
        config = Config(pincc=PinccConfig(api_id=api_id))

        # 保存配置
        self.save(config)

        console.print(
            f"\n[green]✅ 配置已保存到:[/green] [cyan]{self.get_config_path()}[/cyan]"
        )
        console.print(
            "[dim]Configuration saved successfully![/dim]\n",
        )

        return config

    def update_pincc_api_id(self, api_id: str) -> None:
        """更新 Pincc API ID

        Args:
            api_id: 新的 API ID
        """
        config = self.get()
        config.pincc.api_id = api_id
        self.save(config)


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例

    Returns:
        配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
