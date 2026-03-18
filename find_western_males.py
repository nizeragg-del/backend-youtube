import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def find_males():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    found = []
    # Heuristic for non-Korean: Names with common western letters patterns, 
    # and not having common Korean syllables like 'jae', 'seok', 'hyun', etc.
    korean_syllables = ["jae", "seok", "hyun", "jin", "suk", "won", "soo", "young", "choi", "jung", "min", "hoon", "seung", "dong", "joon", "hae", "woo", "beom", "kun"]
    
    for v in voices:
        if v.gender == "male" and v.age in ["middle_age", "senior", "adult"]:
            name = v.voice_name.lower()
            if not any(s in name for s in korean_syllables):
                found.append(v)
            
    print(f"{'ID':<35} | {'Nome':<15}")
    print("-" * 50)
    for v in found:
        print(f"{v.voice_id:<35} | {v.voice_name:<15}")

if __name__ == "__main__":
    find_males()
