import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def find_by_prefix():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    prefix = "tc_5f8"
    
    found = [v for v in voices if v.voice_id.startswith(prefix)]
    
    print(f"Voices starting with {prefix}:")
    for v in found:
        print(f"{v.voice_id} | {v.voice_name}")

if __name__ == "__main__":
    find_by_prefix()
