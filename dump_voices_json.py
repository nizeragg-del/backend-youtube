import os
import json
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def dump_voices():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    raw_list = []
    for v in voices:
        try:
            # Try to get the raw dict if possible
            if hasattr(v, "model_dump"):
                raw_list.append(v.model_dump())
            elif hasattr(v, "to_dict"):
                raw_list.append(v.to_dict())
            else:
                # Manual decomposition
                d = {}
                for attr in dir(v):
                    if not attr.startswith("_") and not callable(getattr(v, attr)):
                        d[attr] = str(getattr(v, attr))
                raw_list.append(d)
        except Exception as e:
            print(f"Error on {v.voice_id}: {e}")
            
    with open("voices_raw.json", "w", encoding="utf-8") as f:
        json.dump(raw_list, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    dump_voices()
