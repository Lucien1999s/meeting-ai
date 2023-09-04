import logging
import time
import requests
from openai import OpenAIError

logging.basicConfig(level=logging.INFO)

def _call_azure_api(prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str:
    url = "https://bigdata-openai-gpt-2.openai.azure.com/openai/deployments/bigdata-gpt35-2/chat/completions?api-version=2023-05-15"
    headers = {"api-key": "3f5c8ab3de1545059600c578e3d96452"}
    
    json_body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    retries = 3
    for retry in range(retries):
        try:
            response = requests.post(url, headers=headers, json=json_body)
            response = response.json()
            choices = response.get("choices", [])
            
            if choices:
                content = choices[0].get("message", {}).get("content")
                if content:
                    prompt_tokens = response["usage"]["prompt_tokens"]
                    completion_tokens = response["usage"]["completion_tokens"]
                    cost = _count_cost("gpt-3.5-turbo", prompt_tokens, completion_tokens)
                    logging.info("Cost: %f", cost)
                    return content
                else:
                    logging.error("No content found in response.")
            else:
                logging.error("No choices found in response.")
            
            if retry == retries - 1:
                logging.error("Failed to generate a response after %d attempts. Aborting.", retries)
                raise
            logging.warning("Retrying (%d/%d) after 10 seconds...", retry + 1, retries)
            time.sleep(10)
        except OpenAIError as error:
            logging.error("Error: %s", error)
            if retry == retries - 1:
                logging.error("Failed to generate a response after %d attempts. Aborting.", retries)
                raise
            logging.warning("Retrying (%d/%d) after 10 seconds...", retry + 1, retries)
            time.sleep(10)

def _count_cost(model: str, prompt_tokens: float, completion_tokens: float) -> float:
    if model == "gpt-3.5-turbo":
        return (prompt_tokens / 1000) * 0.0015 + (completion_tokens / 1000) * 0.002
    return (prompt_tokens / 1000) * 0.003 + (completion_tokens / 1000) * 0.004

res = _call_azure_api("妳好嗎", "妳要naughty的回答", 0.8, 200)
print(res)
