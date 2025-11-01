"""使用量抓取器 - Usage Fetcher

从 claude.ai/settings/usage 抓取使用量数据
"""
from datetime import datetime
from typing import Optional

from playwright.async_api import Page, Response

from .browser import MCPBrowserService
from .models import UsageData


class UsageFetcher:
    """使用量抓取器 - Usage Fetcher

    连接到 Claude 网站并抓取使用量数据
    """

    def __init__(self, cdp_url: str = "http://localhost:9222"):
        """初始化抓取器

        Args:
            cdp_url: Chrome DevTools Protocol URL
        """
        self.browser_service = MCPBrowserService(cdp_url=cdp_url)
        self._usage_api_response: Optional[dict] = None

    async def _intercept_usage_api(self, response: Response) -> None:
        """拦截使用量 API 响应 - Intercept usage API response

        Args:
            response: 网络响应对象
        """
        # 检查是否是使用量 API 请求
        # 注意：实际的 API 端点需要通过浏览器调试确认
        if "usage" in response.url or "consumption" in response.url:
            try:
                data = await response.json()
                self._usage_api_response = data
            except Exception:
                # 忽略非 JSON 响应
                pass

    async def fetch_current(self) -> UsageData:
        """获取当前使用量 - Fetch current usage

        Returns:
            UsageData: 使用量数据

        Raises:
            Exception: 如果无法获取数据
        """
        context = await self.browser_service.get_context()
        page = await context.new_page()

        try:
            # 设置响应拦截器
            page.on("response", self._intercept_usage_api)

            # 导航到使用量页面
            await page.goto("https://claude.ai/settings/usage", wait_until="networkidle")

            # 等待页面加载完成
            await page.wait_for_timeout(2000)  # 等待 2 秒确保 API 请求完成

            # TODO: 实际实现需要根据真实 API 响应结构解析数据
            # 当前使用模拟数据作为原型
            if self._usage_api_response:
                # 如果拦截到 API 响应，尝试解析
                usage_data = self._parse_api_response(self._usage_api_response)
            else:
                # 降级方案：从页面 DOM 提取数据
                usage_data = await self._extract_from_dom(page)

            return usage_data

        finally:
            await page.close()
            # 注意：不关闭浏览器，保持连接以便后续使用

    def _parse_api_response(self, api_data: dict) -> UsageData:
        """解析 API 响应 - Parse API response

        Args:
            api_data: API 响应数据

        Returns:
            UsageData: 解析后的使用量数据
        """
        # TODO: 根据实际 API 响应结构解析
        # 这里使用模拟数据结构
        return UsageData(
            billing_period=api_data.get("billing_period", "2025-10"),
            period_start=datetime.fromisoformat(
                api_data.get("period_start", datetime.now().isoformat())
            ),
            period_end=datetime.fromisoformat(
                api_data.get("period_end", datetime.now().isoformat())
            ),
            input_tokens_used=api_data.get("input_tokens_used", 0),
            input_tokens_quota=api_data.get("input_tokens_quota", 5000000),
            output_tokens_used=api_data.get("output_tokens_used", 0),
            output_tokens_quota=api_data.get("output_tokens_quota", 2500000),
            total_messages=api_data.get("total_messages", 0),
            fetched_at=datetime.now(),
        )

    async def _extract_from_dom(self, page: Page) -> UsageData:
        """从页面 DOM 提取数据 - Extract data from DOM

        当无法拦截 API 时的降级方案

        Args:
            page: Playwright 页面对象

        Returns:
            UsageData: 提取的使用量数据
        """
        # TODO: 根据实际页面结构提取数据
        # 当前返回模拟数据用于原型测试
        return UsageData(
            billing_period="2025-10",
            period_start=datetime(2025, 10, 1),
            period_end=datetime(2025, 10, 31),
            input_tokens_used=1234567,
            input_tokens_quota=5000000,
            output_tokens_used=654321,
            output_tokens_quota=2500000,
            total_messages=150,
            fetched_at=datetime.now(),
        )

    async def close(self) -> None:
        """关闭浏览器连接 - Close browser connection"""
        await self.browser_service.close()
