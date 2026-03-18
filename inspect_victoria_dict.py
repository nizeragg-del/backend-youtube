import os
import json
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def inspect_victoria():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    vic = next((v for v in voices if v.voice_id == "tc_6777669145604e14c7ff8f03"), None)
    
    if vic:
        print("--- DICT INSPECTION: Victoria ---")
        try:
            if hasattr(vic, "model_dump"):
                print(json.dumps(vic.model_dump(), indent=2))
            elif hasattr(vic, "dict"):
                print(json.dumps(vic.dict(), indent=2))
            else:
                print(json.dumps(vic.__dict__, indent=2))
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Victoria not found!")

if __name__ == "__main__":
    inspect_victoria()
