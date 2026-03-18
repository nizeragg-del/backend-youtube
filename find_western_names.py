import os
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def find_western():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    # Simple heuristic: names that don't look Korean (usually short, vowels-syllable pattern)
    # Actually, let's just search for known common names
    common_names = ["Julia", "Gabriel", "Ricardo", "Fernanda", "Rodrigo", "Maria", "Ana", "Luana", "Felipe", "Thiago", "Vitoria", "Gustavo", "Pedro", "Joao", "Beatriz", "Lucas", "Mariana", "Bruna", "Eduardo", "Rafael", "Andre", "Paulo", "Carlos"]
    
    found = []
    for v in voices:
        if any(n.lower() in v.voice_name.lower() for n in common_names):
            found.append(v)
            
    print(f"{'ID':<35} | {'Nome':<15}")
    print("-" * 50)
    for v in found:
        print(f"{v.voice_id:<35} | {v.voice_name:<15}")

if __name__ == "__main__":
    find_western()
