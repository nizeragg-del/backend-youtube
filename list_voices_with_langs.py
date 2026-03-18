import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def list_with_langs():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    with open("voices_with_langs.txt", "w", encoding="utf-8") as f:
        for v in voices:
            lang = "Unknown"
            try:
                if v.languages:
                    lang = v.languages[0].language_code
            except: pass
            f.write(f"{v.voice_id} | {v.voice_name:<15} | {lang}\n")

if __name__ == "__main__":
    list_with_langs()
