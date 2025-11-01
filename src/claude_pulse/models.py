"""数据模型 - Data Models

定义 Claude 使用量相关的数据结构
"""
from datetime import datetime

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
