import os
from dotenv import load_dotenv
from typecast import Typecast
import json

load_dotenv()

def find_portuguese_voices():
    api_key = os.getenv("TYPECAST_API_KEY")
    client = Typecast(api_key=api_key)
    
    print("Buscando vozes via lib Typecast (voices_v2)...")
    try:
        voices = client.voices_v2()
    except Exception as e:
        print(f"Erro ao buscar vozes: {e}")
        return

    print(f"Total de vozes encontradas: {len(voices)}")
    
    keywords = ["Portuguese", "Português", "pt-BR", "pt-PT", "pt_BR", "pt_PT", "Brazil", "Brasil"]
    found_any = False
    
    for v in voices:
        # Tentar converter o objeto para string/json para busca universal em todos os campos
        try:
            # A lib pode ter atributos específicos
            v_data = {
                "name": getattr(v, "voice_name", ""),
                "id": getattr(v, "actor_id", ""),
                "description": getattr(v, "description", ""),
                "tags": getattr(v, "tags", [])
            }
            v_str = json.dumps(v_data, ensure_ascii=False).lower()
        except:
            v_str = str(v).lower()
            
        if any(k.lower() in v_str for k in keywords):
            print(f"--- ACHOU: {getattr(v, 'voice_name', 'Sem Nome')} ---")
            print(f"ID: {getattr(v, 'actor_id', 'Sem ID')}")
            print(f"Desc: {getattr(v, 'description', '')}")
            print(f"Tags: {getattr(v, 'tags', [])}")
            found_any = True
            
    if not found_any:
        print("\nNenhuma voz com tags explícitas de Português encontrada além das já conhecidas (se houver).")

if __name__ == "__main__":
    find_portuguese_voices()
