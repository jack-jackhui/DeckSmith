import os
import json
import requests
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()

azure_dalle_api_key = os.getenv("AZURE_DALLE_API_KEY")
azure_dalle_endpoint = os.getenv("AZURE_DALLE_ENDPOINT")
azure_dalle_api_version = os.getenv("AZURE_DALLE_API_VERSION")
azure_dalle_deployment_name = os.getenv("AZURE_DALLE_DEPLOYMENT_NAME")
azure_dalle_model_name = os.getenv("AZURE_DALLE_MODEL_NAME")

DALLE3_PROMPT = '''
Create a supporting image for the following topic: {topic}
Use the following as reference only, it need not be visualized or have an impact on the image generation directly: 
{key_points}
'''

# Initialize the Azure OpenAI client
llm = AzureOpenAI(
    api_version=azure_dalle_api_version,
    azure_endpoint=azure_dalle_endpoint,
    api_key=azure_dalle_api_key
)

def generate_cover(page, module):
    key_points_str = ""
    for point in module["key_points"]:
        key_points_str += f"{point} \n"

    prompt = DALLE3_PROMPT.format(
        topic=module["topic"], key_points=key_points_str)

    result = llm.images.generate(
        model=azure_dalle_deployment_name,
        prompt=prompt,
        size="1024x1792",
        quality="standard",
        n=1
    )

    image_url = json.loads(result.model_dump_json())['data'][0]['url']

    response = requests.get(image_url)
    os.makedirs("images", exist_ok=True)  # Create the images directory if it doesn't exist
    filename = f"images/image_{page}.jpg"
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
    else:
        print("Failed to download image:", response.status_code)
        filename = None

    module["filename"] = filename

    return module