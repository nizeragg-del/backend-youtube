import os
import json
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def debug_pt_br():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    # Let's find Camila first to see her structure
    camila = next((v for v in voices if "Camila" in v.voice_name), None)
    if camila:
        print("Camila found!")
        # Try to see all attributes
        for attr in dir(camila):
            if not attr.startswith("_"):
                try:
                    val = getattr(camila, attr)
                    print(f"  {attr}: {val}")
                except: pass
                
        if hasattr(camila, "languages"):
            print(f"  Languages: {camila.languages}")
            for l in camila.languages:
                print(f"    Code: {l.language_code}")
    
    print("\nSearching for others with pt-BR...")
    count = 0
    for v in voices:
        is_br = False
        try:
            for l in v.languages:
                if l.language_code == "pt-BR":
                    is_br = True
                    break
        except: pass
        
        if is_br:
            print(f"Found: {v.voice_id} | {v.voice_name}")
            count += 1
            if count >= 10: break

if __name__ == "__main__":
    debug_pt_br()
