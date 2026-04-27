import logging

import uvicorn

from llmr.app import app
from llmr.config import settings

if __name__ == "__main__":
    if settings.app_host == "0.0.0.0":
        logging.warning(
            "LLM-r is binding to all interfaces (0.0.0.0). "
            "Set LLMR_HOST=127.0.0.1 for local-only access."
        )
    elif settings.app_host not in ("127.0.0.1", "localhost"):
        logging.warning(
            "LLM-r is running on a public interface (%s). "
            "Consider binding to 127.0.0.1 for local use.",
            settings.app_host,
        )
    logging.info("Starting LLM-r at http://%s:%d", settings.app_host, settings.app_port)
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
