
import re

def find_image_url(obj):
    if isinstance(obj, str):
        match = re.search(r'(https?://\S+\.(?:png|jpg|jpeg|webp|gif))', obj, re.IGNORECASE)
        return match.group(1) if match else None
    if isinstance(obj, list):
        for item in obj:
            url = find_image_url(item)
            if url: return url
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k not in ["prompt", "agentProfile"]:
                url = find_image_url(v)
                if url: return url
    return None

test_cases = [
    {
        "name": "Nested in messages",
        "data": {"status": "completed", "result": {"messages": [{"content": "https://example.com/image.png"}]}}
    },
    {
        "name": "Direct in output",
        "data": {"task_status": "DONE", "output": "Image generated: https://example.com/pic.jpg"}
    },
    {
        "name": "Deeply nested",
        "data": {"a": {"b": [{"c": "https://example.com/test.webp"}]}}
    }
]

for case in test_cases:
    url = find_image_url(case["data"])
    print(f"Test '{case['name']}': {'OK' if url else 'FAILED'}")
