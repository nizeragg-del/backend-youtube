import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def list_all():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    with open("all_voices_simple.txt", "w", encoding="utf-8") as f:
        for v in voices:
            f.write(f"{v.voice_id} | {v.voice_name}\n")

if __name__ == "__main__":
    list_all()
