import os
import json
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def inspect_camila():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    camila = next((v for v in voices if "Camila" in v.voice_name), None)
    
    if camila:
        print("--- Inspecting Camila ---")
        # Print all attributes
        for attr in dir(camila):
            if not attr.startswith("__"):
                try:
                    val = getattr(camila, attr)
                    print(f"{attr}: {val}")
                except:
                    pass
        
        # Try to see if there's a __dict__ or similar
        try:
            print("\n--- Dict representation ---")
            print(json.dumps(camila.to_dict(), indent=2))
        except:
            print("\nNo to_dict() method")

if __name__ == "__main__":
    inspect_camila()
