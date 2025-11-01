"""使用量抓取器 - Usage Fetcher

从 claude.ai/settings/usage 抓取使用量数据
"""
from datetime import datetime

from playwright.async_api import Page

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

    async def fetch_current(self) -> UsageData:
        """获取当前使用量 - Fetch current usage

        从 claude.ai/settings/usage 页面直接提取显示的信息。
        在后台标签页中执行，获取数据后立即关闭，尽量减少对用户浏览的干扰。

        Returns:
            UsageData: 使用量数据

        Raises:
            Exception: 如果无法获取数据
        """
        # 使用共享的浏览器上下文（保持登录态）
        context = await self.browser_service.get_context()

        # 创建新标签页（后台）
        page = await context.new_page()

        try:
            # 导航到使用量页面
            await page.goto(
                "https://claude.ai/settings/usage", wait_until="networkidle"
            )

            # 从页面 DOM 提取数据
            usage_data = await self._extract_from_dom(page)

            return usage_data

        finally:
            # 立即关闭标签页，减少干扰
            await page.close()

    async def _extract_from_dom(self, page: Page) -> UsageData:
        """从页面 DOM 提取数据 - Extract data from DOM

        提取页面上显示的关键信息：
        - Plan usage limits
        - Current session
        - 使用百分比 (10% used)
        - 重置时间 (Resets in 3 hr 16 min)
        - 最后更新 (Last updated: 1 minute ago)

        Args:
            page: Playwright 页面对象

        Returns:
            UsageData: 提取的使用量数据
        """
        # 等待页面内容加载（减少等待时间以快速完成）
        await page.wait_for_timeout(1500)

        # 使用 JavaScript 提取页面文本内容
        page_text = await page.evaluate("""
            () => {
                const text = document.body.innerText;
                return text;
            }
        """)

        # 解析关键信息
        plan_type = "Plan usage limits"  # 默认值
        session_type = "Current session"  # 默认值
        usage_percent = 0.0
        reset_time = "Unknown"
        last_updated = "Unknown"

        # 提取使用百分比 - 匹配 "10% used" 或 "10 % used"
        import re

        usage_match = re.search(r"(\d+)\s*%\s*used", page_text, re.IGNORECASE)
        if usage_match:
            usage_percent = float(usage_match.group(1))

        # 提取重置时间 - 匹配 "Resets in 3 hr 16 min"
        reset_match = re.search(
            r"Resets in\s+(.+?)(?:\n|$)", page_text, re.IGNORECASE
        )
        if reset_match:
            reset_time = reset_match.group(1).strip()

        # 提取最后更新时间 - 匹配 "Last updated: 1 minute ago"
        updated_match = re.search(
            r"Last updated:\s+(.+?)(?:\n|$)", page_text, re.IGNORECASE
        )
        if updated_match:
            last_updated = updated_match.group(1).strip()

        # 检查计划类型
        if "Plan usage limits" in page_text:
            plan_type = "Plan usage limits"
        elif "plan" in page_text.lower():
            # 尝试提取实际的计划名称
            plan_match = re.search(r"([\w\s]+plan[\w\s]*)", page_text, re.IGNORECASE)
            if plan_match:
                plan_type = plan_match.group(1).strip()

        # 检查会话类型
        if "Current session" in page_text:
            session_type = "Current session"

        return UsageData(
            plan_type=plan_type,
            session_type=session_type,
            usage_percent=usage_percent,
            reset_time=reset_time,
            last_updated=last_updated,
            fetched_at=datetime.now(),
        )

    async def close(self) -> None:
        """关闭浏览器连接 - Close browser connection"""
        await self.browser_service.close()
