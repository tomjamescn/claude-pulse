"""第三方 API 获取器 - Third-party API Fetcher

从第三方 Claude API 服务获取使用量数据
"""
from datetime import datetime
from typing import Any, Dict

import httpx

from .models import ThirdPartyLimit, ThirdPartyUsageData


class ThirdPartyFetcher:
    """第三方 API 使用量获取器 - Third-party API Usage Fetcher

    通过 HTTP 请求获取第三方 Claude API 服务的使用量信息
    """

    # 默认配置 - 固化的 API 配置
    DEFAULT_API_URL = "https://hk1.pincc.ai/apiStats/api/user-stats"
    DEFAULT_API_ID = "719b5189-1855-4982-9331-a15927e34525"

    def __init__(
        self,
        api_url: str = None,
        api_id: str = None,
    ):
        """初始化获取器

        Args:
            api_url: API 端点 URL（可选，默认使用固化的 URL）
            api_id: API ID（可选，默认使用固化的 ID）
        """
        self.api_url = api_url or self.DEFAULT_API_URL
        self.api_id = api_id or self.DEFAULT_API_ID

    async def fetch_usage(self) -> ThirdPartyUsageData:
        """获取使用量数据 - Fetch usage data

        Returns:
            ThirdPartyUsageData: 使用量数据

        Raises:
            Exception: 如果无法获取数据
        """
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://hk1.pincc.ai",
            "pragma": "no-cache",
            "referer": f"https://hk1.pincc.ai/admin-next/api-stats?apiId={self.api_id}",
            "user-agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
            ),
        }

        payload = {"apiId": self.api_id}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url, headers=headers, json=payload, timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

        # 解析响应数据
        return self._parse_response(data)

    def _parse_response(self, data: Dict[str, Any]) -> ThirdPartyUsageData:
        """解析 API 响应 - Parse API response

        Args:
            data: API 响应数据

        Returns:
            ThirdPartyUsageData: 解析后的使用量数据
        """
        # 实际数据在 data.data.limits 中
        api_data = data.get("data", {})
        limits = api_data.get("limits", {})

        # 解析各种限制
        daily_limit = None
        total_limit = None
        time_window_limit = None
        total_cost = limits.get("currentTotalCost", 0.0)

        # 解析每日限制
        daily_cost_limit = limits.get("dailyCostLimit", 0)
        current_daily_cost = limits.get("currentDailyCost", 0.0)
        if daily_cost_limit > 0:
            daily_limit = ThirdPartyLimit(
                type="Daily Limit",
                value=daily_cost_limit,
                used=current_daily_cost,
                remaining=daily_cost_limit - current_daily_cost
                if daily_cost_limit > 0
                else None,
                unit="USD",
            )

        # 解析总限制
        total_cost_limit = limits.get("totalCostLimit", 0)
        current_total_cost = limits.get("currentTotalCost", 0.0)
        if total_cost_limit > 0:
            total_limit = ThirdPartyLimit(
                type="Total Limit",
                value=total_cost_limit,
                used=current_total_cost,
                remaining=total_cost_limit - current_total_cost
                if total_cost_limit > 0
                else None,
                unit="USD",
            )

        # 解析时间窗口信息
        window_start_time_ms = limits.get("windowStartTime")
        window_end_time_ms = limits.get("windowEndTime")
        window_remaining_seconds = limits.get("windowRemainingSeconds", 0)

        # 转换时间戳（毫秒）为 datetime
        window_start_time = None
        window_end_time = None
        if window_start_time_ms:
            window_start_time = datetime.fromtimestamp(window_start_time_ms / 1000)
        if window_end_time_ms:
            window_end_time = datetime.fromtimestamp(window_end_time_ms / 1000)

        # 解析时间窗口限制 (rateLimitCost)
        rate_limit_cost = limits.get("rateLimitCost", 0)
        current_window_cost = limits.get("currentWindowCost", 0.0)
        if rate_limit_cost > 0:
            time_window_limit = ThirdPartyLimit(
                type="Time Window Limit",
                value=rate_limit_cost,
                used=current_window_cost,
                remaining=rate_limit_cost - current_window_cost
                if rate_limit_cost > 0
                else None,
                unit="USD",
            )

        return ThirdPartyUsageData(
            api_id=self.api_id,
            daily_limit=daily_limit,
            total_limit=total_limit,
            time_window_limit=time_window_limit,
            window_start_time=window_start_time,
            window_end_time=window_end_time,
            window_remaining_seconds=window_remaining_seconds,
            total_cost=total_cost,
            fetched_at=datetime.now(),
        )
