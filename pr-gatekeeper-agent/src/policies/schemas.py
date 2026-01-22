from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class ToolTimeouts(BaseModel):
    ruff: int = 60
    pytest: int = 600
    ripgrep: int = 30


class FailStrategy(BaseModel):
    on_tool_error: str = "closed"


class Thresholds(BaseModel):
    block_on_severity_at_or_above: str = "HIGH"


class EnabledTools(BaseModel):
    ruff: bool = True
    pytest: bool = True
    ripgrep: bool = True


class ReportConfig(BaseModel):
    max_stdout_chars: int = 2000


class PolicyConfig(BaseModel):
    tool_timeouts: ToolTimeouts = Field(default_factory=ToolTimeouts)
    fail_strategy: FailStrategy = Field(default_factory=FailStrategy)
    thresholds: Thresholds = Field(default_factory=Thresholds)
    enabled_tools: EnabledTools = Field(default_factory=EnabledTools)
    report: ReportConfig = Field(default_factory=ReportConfig)

    @classmethod
    def from_dict(cls, data: Dict) -> "PolicyConfig":
        return cls(**data)
