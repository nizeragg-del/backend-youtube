import os
import json
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def list_v1():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    # In some versions, client.voices() returns a list of voices
    try:
        voices = client.voices()
        print(f"Total v1 voices: {len(voices)}")
        if len(voices) > 0:
            first = voices[0]
            print("--- V1 FIRST VOICE ---")
            if hasattr(first, "model_dump"):
                print(json.dumps(first.model_dump(), indent=2))
            elif hasattr(first, "dict"):
                print(json.dumps(first.dict(), indent=2))
            else:
                print(first)
                
            # Search for Brazilian names in v1
            br_names = ["camila", "ricardo", "fernanda", "gabriel", "julia", "rodrigo"]
            found = []
            for v in voices:
                if any(n in v.voice_name.lower() for n in br_names):
                    found.append(v)
            
            print(f"\nFound {len(found)} Brazilian names in v1:")
            for v in found:
                print(f"{v.voice_id} | {v.voice_name}")
                
    except Exception as e:
        print(f"Error in v1: {e}")

if __name__ == "__main__":
    list_v1()
