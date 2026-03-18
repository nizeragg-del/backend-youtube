import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def filter_tc5():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    found = []
    for v in voices:
        if v.voice_id.startswith("tc_5"):
            found.append(v)
            
    print(f"{'ID':<35} | {'Nome':<15}")
    print("-" * 50)
    for v in found:
        print(f"{v.voice_id:<35} | {v.voice_name:<15}")

if __name__ == "__main__":
    filter_tc5()
