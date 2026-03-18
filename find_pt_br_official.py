import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def find_br():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    # Check if there's a filter in voices_v2 or similar
    # According to some versions of typecast-python, we might need to check v.locales or similar
    
    voices = client.voices_v2()
    
    print(f"{'ID':<35} | {'Nome':<15} | {'Attributes'}")
    print("-" * 80)
    
    found = 0
    for v in voices:
        # If we see any attribute that sounds like language
        attrs = dir(v)
        is_portuguese = False
        
        # Check by name first as heuristic
        if v.voice_name.lower() in ["camila", "julia", "gabriel", "ricardo", "fernanda", "rodrigo"]:
            is_portuguese = True
            
        if is_portuguese:
            print(f"{v.voice_id:<35} | {v.voice_name:<15} | {v.age}, {v.gender}")
            found += 1
            
    print(f"\nTotal potential: {found}")

if __name__ == "__main__":
    find_br()
