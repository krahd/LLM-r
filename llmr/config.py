import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    ableton_host: str = Field(default=os.getenv("LLMR_ABLETON_HOST", "127.0.0.1"))
    ableton_port: int = Field(default=int(os.getenv("LLMR_ABLETON_PORT", "11000")))
    modelito_model: str = Field(default=os.getenv("LLMR_MODEL", "gpt-4.1-mini"))
    modelito_provider: str = Field(default=os.getenv("LLMR_PROVIDER", "openai"))
    app_host: str = Field(default=os.getenv("LLMR_HOST", "0.0.0.0"))
    app_port: int = Field(default=int(os.getenv("LLMR_PORT", "8787")))
    plan_store_path: str = Field(default=os.getenv("LLMR_PLAN_STORE_PATH", ".llmr/plans.json"))
<<<<<<< HEAD
=======
    plan_store_path: str = Field(default=os.getenv("LLMR_PLAN_STORE_PATH", ".llmr/plans.json"))
>>>>>>> pr-2


settings = Settings()
