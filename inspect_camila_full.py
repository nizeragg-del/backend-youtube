import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def inspect_full():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    camila = next((v for v in voices if "Camila" in v.voice_name), None)
    
    if camila:
        print(f"--- FULL INSPECTION: {camila.voice_name} ---")
        for attr in dir(camila):
            if not attr.startswith("_"):
                try:
                    val = getattr(camila, attr)
                    print(f"{attr}: {val}")
                except Exception as e:
                    print(f"{attr}: [Error: {e}]")
    else:
        print("Camila not found!")

if __name__ == "__main__":
    inspect_full()
