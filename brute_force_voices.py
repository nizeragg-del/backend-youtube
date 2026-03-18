import os
import json
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def brute_force_find():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    found = []
    for v in voices:
        match = False
        details = {}
        for attr in dir(v):
            if not attr.startswith("_"):
                try:
                    val = getattr(v, attr)
                    val_str = str(val).lower()
                    if "portuguese" in val_str or "brazil" in val_str or "pt-br" in val_str:
                        match = True
                        details[attr] = str(val)
                except: pass
        if match:
            found.append({
                "id": v.voice_id,
                "name": v.voice_name,
                "matches": details
            })
            
    print(json.dumps(found, indent=2))

if __name__ == "__main__":
    brute_force_find()
