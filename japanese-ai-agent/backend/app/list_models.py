import json
import urllib.request

from app.config import HF_TOKEN

req = urllib.request.Request(
    "https://router.huggingface.co/v1/models",
    headers={"Authorization": f"Bearer {HF_TOKEN}"},
)
with urllib.request.urlopen(req) as r:
    data = json.load(r)

for m in data["data"]:
    print(m["id"])