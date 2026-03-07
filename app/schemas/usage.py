from pydantic import BaseModel

class UsageStats(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    totalTokens: int
    totalPrompts: int = 1
    estimated_cost_usd: float
    model: str
