import os
import json
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def inspect_carlos():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    carlos = next((v for v in voices if "Carlos" in v.voice_name), None)
    
    if carlos:
        print(f"Carlos ID: {carlos.voice_id}")
        # Try to find language
        for attr in dir(carlos):
            if not attr.startswith("_"):
                try:
                    val = getattr(carlos, attr)
                    print(f"  {attr}: {val}")
                except: pass
                
if __name__ == "__main__":
    inspect_carlos()
