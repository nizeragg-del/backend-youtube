import os
import json
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def inspect_dict():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    camila = next((v for v in voices if "Camila" in v.voice_name), None)
    
    if camila:
        print("--- DICT INSPECTION: Camila ---")
        try:
            # Typecast SDK uses Pydantic
            if hasattr(camila, "model_dump"):
                print(json.dumps(camila.model_dump(), indent=2))
            elif hasattr(camila, "dict"):
                print(json.dumps(camila.dict(), indent=2))
            else:
                print(json.dumps(camila.__dict__, indent=2))
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Camila not found!")

if __name__ == "__main__":
    inspect_dict()
