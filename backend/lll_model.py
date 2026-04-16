import logging
import os

from agents.extensions.models.litellm_model import LitellmModel
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"), override=True)
logger = logging.getLogger()


def get_model():
    """Get the model from the environment variables."""
    api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    base_url: str | None = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )
    model: str | None = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
    if not api_key:
        logger.error("OPENROUTER_API_KEY must be set")
        return None
    return LitellmModel(model=model, api_key=api_key, base_url=base_url)


model: LitellmModel = get_model()
model_id: str = model.model
