import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

def generate_ai_summary(metrics):
    """
    Generate business insights from metrics using Azure GitHub Inference API
    """
    endpoint = "https://models.github.ai/inference"
    model_name = "openai/gpt-4o"
    token = os.getenv("OPENAI_API_KEY")

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )

    prompt = f"""You are a SaaS growth analyst. Analyze these user metrics:
{metrics}

Provide:
1. Data summary in plain English
2. 3 key observations
3. 2 actionable recommendations
Format: Markdown"""

    response = client.complete(
        messages=[
            SystemMessage("You are an expert SaaS business analyst"),
            UserMessage(prompt),
        ],
        temperature=0.3,
        top_p=1.0,
        max_tokens=1000,
        model=model_name
    )

    return response.choices[0].message.content
