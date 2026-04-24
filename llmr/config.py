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
    api_key: str = Field(default=os.getenv("LLMR_API_KEY", ""))
    require_auth: bool = Field(default=bool(int(os.getenv("LLMR_REQUIRE_AUTH", "0"))))
    # Remote script (Ableton MIDI Remote Script) bridge settings
    remote_script_enabled: bool = Field(default=bool(int(os.getenv("LLMR_USE_REMOTE_SCRIPT", "0"))))
    remote_script_host: str = Field(default=os.getenv("LLMR_REMOTE_HOST", "127.0.0.1"))
    remote_script_port: int = Field(default=int(os.getenv("LLMR_REMOTE_PORT", "20000")))
    osc_listen_host: str = Field(default=os.getenv("LLMR_OSC_HOST", "127.0.0.1"))
    osc_listen_port: int = Field(default=int(os.getenv("LLMR_OSC_PORT", "9000")))
    enable_osc_server: bool = Field(default=bool(int(os.getenv("LLMR_ENABLE_OSC_SERVER", "1"))))


settings = Settings()
