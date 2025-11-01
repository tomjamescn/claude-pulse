"""数据模型 - Data Models

定义 Claude 使用量相关的数据结构
"""
from datetime import datetime

from pydantic import BaseModel, Field, computed_field


class UsageData(BaseModel):
    """Claude 使用量数据 - Claude usage data

    从 claude.ai/settings/usage 获取的使用量信息
    """
    billing_period: str = Field(..., description="计费周期，如 '2025-10'")
    period_start: datetime = Field(..., description="周期开始时间")
    period_end: datetime = Field(..., description="周期结束时间")
    input_tokens_used: int = Field(ge=0, description="已使用输入 tokens")
    input_tokens_quota: int = Field(gt=0, description="输入 tokens 配额")
    output_tokens_used: int = Field(ge=0, description="已使用输出 tokens")
    output_tokens_quota: int = Field(gt=0, description="输出 tokens 配额")
    total_messages: int = Field(ge=0, description="总消息数")
    fetched_at: datetime = Field(default_factory=datetime.now, description="获取时间")

    @computed_field
    @property
    def input_usage_percent(self) -> float:
        """输入 tokens 使用百分比 - Input tokens usage percentage"""
        if self.input_tokens_quota == 0:
            return 0.0
        return (self.input_tokens_used / self.input_tokens_quota) * 100

    @computed_field
    @property
    def output_usage_percent(self) -> float:
        """输出 tokens 使用百分比 - Output tokens usage percentage"""
        if self.output_tokens_quota == 0:
            return 0.0
        return (self.output_tokens_used / self.output_tokens_quota) * 100

    @computed_field
    @property
    def overall_usage_percent(self) -> float:
        """整体使用百分比 - Overall usage percentage (average of input and output)"""
        return (self.input_usage_percent + self.output_usage_percent) / 2

    @computed_field
    @property
    def is_high_usage(self) -> bool:
        """是否高使用量（超过80%） - Whether usage is high (over 80%)"""
        return self.overall_usage_percent >= 80.0
