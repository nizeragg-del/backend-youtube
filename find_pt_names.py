import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def find_by_name():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    names_to_find = ["Julia", "Fernanda", "Gabriel", "Ricardo", "Rodrigo", "Beatriz", "Lucas", "Mariana"]
    
    print(f"{'ID':<35} | {'Nome':<15}")
    print("-" * 50)
    
    for v in voices:
        if any(name.lower() in v.voice_name.lower() for name in names_to_find):
            print(f"{v.voice_id:<35} | {v.voice_name:<15}")

if __name__ == "__main__":
    find_by_name()
