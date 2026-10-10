from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from app.config import HF_TOKEN, HF_MODEL

print("Model:", HF_MODEL, "| token_set:", bool(HF_TOKEN))

client = InferenceClient(api_key=HF_TOKEN, timeout=60)

try:
    r = client.chat.completions.create(
        model=HF_MODEL,
        messages=[{"role": "user", "content": "Say hello in Japanese."}],
        max_tokens=50,
    )
    print("OK:", r.choices[0].message.content)
except HfHubHTTPError as e:
    resp = e.response
    print("STATUS:", resp.status_code if resp is not None else None)
    print("BODY:", resp.text if resp is not None else str(e))
except Exception as e:
    print(type(e).__name__, e)