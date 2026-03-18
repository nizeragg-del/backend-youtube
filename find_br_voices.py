import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def find_br():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    print(f"{'ID':<35} | {'Nome':<15} | {'Langs'}")
    print("-" * 60)
    
    count = 0
    for v in voices:
        try:
            langs = [lang.language_code for lang in v.languages]
            if "pt-BR" in langs:
                print(f"{v.voice_id:<35} | {v.voice_name:<15} | {','.join(langs)}")
                count += 1
        except:
            pass
            
    print(f"\nTotal pt-BR found: {count}")

if __name__ == "__main__":
    find_br()
