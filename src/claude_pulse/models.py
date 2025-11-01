"""数据模型 - Data Models

定义 Claude 使用量相关的数据结构
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UsageData(BaseModel):
    """Claude 使用量数据 - Claude usage data

    从 claude.ai/settings/usage 页面提取的简化信息
    """
    plan_type: str = Field(..., description="计划类型，如 'Plan usage limits'")
    session_type: str = Field(..., description="会话类型，如 'Current session'")
    usage_percent: float = Field(ge=0, le=100, description="使用百分比，如 10.0 表示 10%")
    reset_time: str = Field(..., description="重置时间，如 '3 hr 16 min'")
    last_updated: str = Field(..., description="最后更新时间，如 '1 minute ago'")
    fetched_at: datetime = Field(
        default_factory=datetime.now, description="数据获取时间"
    )


class ThirdPartyLimit(BaseModel):
    """第三方 API 限制信息 - Third-party API limit"""
    type: str = Field(..., description="限制类型")
    value: float = Field(..., description="限制值")
    used: float = Field(default=0.0, description="已使用量")
    remaining: Optional[float] = Field(None, description="剩余量")
    unit: str = Field(default="USD", description="单位")


class ThirdPartyUsageData(BaseModel):
    """第三方 Claude API 使用量数据 - Third-party Claude API usage data

    从第三方 API 获取的使用量信息
    """
    api_id: str = Field(..., description="API ID")
    daily_limit: Optional[ThirdPartyLimit] = Field(None, description="每日费用限制")
    total_limit: Optional[ThirdPartyLimit] = Field(None, description="总费用限制")
    opus_weekly_limit: Optional[ThirdPartyLimit] = Field(
        None, description="Opus 模型周费用限制"
    )
    time_window_limit: Optional[ThirdPartyLimit] = Field(
        None, description="时间窗口限制"
    )
    total_cost: float = Field(default=0.0, description="总费用")
    fetched_at: datetime = Field(
        default_factory=datetime.now, description="数据获取时间"
    )
