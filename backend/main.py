import uvicorn

from llmr.app import app
from llmr.config import settings


if __name__ == "__main__":
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
