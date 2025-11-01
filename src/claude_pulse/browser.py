"""浏览器服务 - Browser Service

通过 Playwright MCP 扩展连接到已运行的 Chrome 浏览器，复用登录态
"""
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Playwright, async_playwright


class MCPBrowserService:
    """MCP 浏览器服务 - MCP Browser Service

    连接到 Playwright MCP Chrome Extension，复用已登录的浏览器会话
    """

    def __init__(self, cdp_url: str = "http://localhost:9222"):
        """初始化浏览器服务

        Args:
            cdp_url: Chrome DevTools Protocol URL，默认 localhost:9222
        """
        self.cdp_url = cdp_url
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

    async def connect(self) -> None:
        """连接到浏览器 - Connect to browser

        Raises:
            Exception: 如果无法连接到 Chrome
        """
        if self._playwright is None:
            self._playwright = await async_playwright().start()

        if self._browser is None:
            # 连接到已运行的 Chrome（通过 CDP）
            self._browser = await self._playwright.chromium.connect_over_cdp(self.cdp_url)

    async def get_context(self) -> BrowserContext:
        """获取浏览器上下文 - Get browser context

        复用现有的浏览器上下文，保留登录状态

        Returns:
            BrowserContext: 浏览器上下文

        Raises:
            Exception: 如果浏览器未连接或没有上下文
        """
        if self._browser is None:
            await self.connect()

        # 使用现有的浏览器上下文（第一个，通常是默认上下文）
        contexts = self._browser.contexts
        if not contexts:
            raise Exception(
                "No browser contexts found. "
                "Please ensure Chrome is running and you are logged into claude.ai"
            )

        self._context = contexts[0]
        return self._context

    async def create_isolated_context(self) -> BrowserContext:
        """创建独立的浏览器上下文 - Create isolated browser context

        创建一个新的浏览器上下文（新窗口），不影响用户当前浏览的标签页。
        该上下文会共享浏览器的登录态（Cookies），但在独立的窗口中运行。

        Returns:
            BrowserContext: 新的独立浏览器上下文

        Raises:
            Exception: 如果浏览器未连接
        """
        if self._browser is None:
            await self.connect()

        # 创建新的浏览器上下文（独立窗口）
        # 注意：这个上下文会共享浏览器的存储状态（Cookies等）
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 720},  # 设置窗口大小
            # 注意：CDP 连接时无法真正隐藏窗口，但可以设置较小尺寸
        )

        return context

    async def close(self) -> None:
        """关闭连接 - Close connection

        注意：不会关闭浏览器本身，只断开连接
        """
        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        self._context = None
