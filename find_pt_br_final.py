import os
import json
from dotenv import load_dotenv
from typecast import Typecast

load_dotenv()

def find_final():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    voices = client.voices_v2()
    
    # Lista de nomes brasileiros prováveis no Typecast
    br_names = ["Camila", "Julia", "Fernanda", "Gabriel", "Ricardo", "Rodrigo", "Beatriz", "Lucas", "Mariana", "Felipe", "Thiago", "Vitoria", "Gustavo", "Pedro", "Joao", "Maria", "Ana", "Luana"]
    
    found = []
    for v in voices:
        if any(n.lower() == v.voice_name.lower() for n in br_names):
            found.append({
                "id": v.voice_id,
                "name": v.voice_name,
                "gender": str(v.gender),
                "age": str(v.age)
            })
            
    print(json.dumps(found, indent=2))

if __name__ == "__main__":
    find_final()
