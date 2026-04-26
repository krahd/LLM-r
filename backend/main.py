import uvicorn

from llmr.app import app
from llmr.config import settings


import logging

if __name__ == "__main__":
    if settings.app_host not in ("127.0.0.1", "localhost", "0.0.0.0"):
        logging.warning(
            f"[SECURITY] LLM-r API is running on a public interface: {settings.app_host}. Consider binding to '127.0.0.1' for local use.")
    elif settings.app_host == "0.0.0.0":
        logging.warning(
            "[SECURITY] LLM-r API is running on all interfaces (0.0.0.0). This may expose your API to the network. Use '127.0.0.1' for local-only access.")
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
