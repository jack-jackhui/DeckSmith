"""Image generation module using Azure DALL-E."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from openai import AzureOpenAI

from constants import (
    IMAGE_DOWNLOAD_TIMEOUT,
    IMAGE_QUALITY,
    IMAGE_SIZE_LANDSCAPE,
)

load_dotenv()

logger = logging.getLogger(__name__)

azure_dalle_api_key: Optional[str] = os.getenv("AZURE_DALLE_API_KEY")
azure_dalle_endpoint: Optional[str] = os.getenv("AZURE_DALLE_ENDPOINT")
azure_dalle_api_version: Optional[str] = os.getenv("AZURE_DALLE_API_VERSION")
azure_dalle_deployment_name: Optional[str] = os.getenv("AZURE_DALLE_DEPLOYMENT_NAME")
azure_dalle_model_name: Optional[str] = os.getenv("AZURE_DALLE_MODEL_NAME")

DALLE3_PROMPT = '''
Create a supporting image for the following topic: {topic}
Use the following as reference only, it need not be visualized or have an impact on the image generation directly:
{key_points}
'''

llm: Optional[AzureOpenAI] = None
if azure_dalle_api_key and azure_dalle_endpoint:
    llm = AzureOpenAI(
        api_version=azure_dalle_api_version,
        azure_endpoint=azure_dalle_endpoint,
        api_key=azure_dalle_api_key
    )


def generate_cover(page: int, module: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a cover image for a slide.

    Args:
        page: The page/slide number.
        module: A dictionary containing 'topic' and 'key_points'.

    Returns:
        The module dictionary with 'filename' added.
    """
    if llm is None:
        logger.error("DALL-E client not initialized. Check API credentials.")
        module["filename"] = None
        return module

    key_points: List[str] = module.get("key_points", [])
    key_points_str = ""
    for point in key_points:
        key_points_str += f"{point} \n"

    prompt = DALLE3_PROMPT.format(
        topic=module.get("topic", ""),
        key_points=key_points_str
    )

    try:
        logger.info("Generating image for page %d with topic: %s", page, module.get("topic", ""))

        result = llm.images.generate(
            model=azure_dalle_deployment_name,
            prompt=prompt,
            size=IMAGE_SIZE_LANDSCAPE,
            quality=IMAGE_QUALITY,
            n=1
        )

        image_data = json.loads(result.model_dump_json())
        image_url = image_data['data'][0]['url']

        os.makedirs("images", exist_ok=True)
        filename = f"images/image_{page}.jpg"

        try:
            response = requests.get(image_url, timeout=IMAGE_DOWNLOAD_TIMEOUT)
            response.raise_for_status()

            with open(filename, "wb") as f:
                f.write(response.content)

            logger.info("Image saved to %s", filename)
            module["filename"] = filename

        except requests.Timeout:
            logger.error("Timeout while downloading image for page %d", page)
            module["filename"] = None
        except requests.RequestException as e:
            logger.error("Failed to download image for page %d: %s", page, e)
            module["filename"] = None

    except Exception as e:
        logger.error("Error generating image for page %d: %s", page, e)
        module["filename"] = None

    return module
