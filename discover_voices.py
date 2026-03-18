import os
import json
from dotenv import load_dotenv

load_dotenv()

def list_all_voices():
    # Carregamento tardio para evitar erro de import se o pacote não estiver lá
    try:
        from typecast import Typecast
    except ImportError:
        print("Erro: typecast-python não está instalado. Rode 'pip install typecast-python'")
        return

    api_key = os.getenv("TYPECAST_API_KEY")
    if not api_key:
        print("Erro: TYPECAST_API_KEY não encontrada no .env")
        return

    client = Typecast(api_key=api_key)
    
    print("Buscando todas as vozes disponíveis no Typecast.ai...")
    try:
        voices = client.voices_v2()
        
        with open("voices_list.txt", "w", encoding="utf-8") as f:
            f.write(f"{'Voz ID':<35} | {'Nome':<20} | {'Gênero':<15} | {'Langs':<20}\n")
            f.write("-" * 95 + "\n")
            for v in voices:
                langs = []
                try:
                    for lang in v.languages:
                        langs.append(lang.language_code)
                except: pass
                lang_str = ",".join(langs)
                line = f"[*] {v.voice_id:<31} | {v.voice_name:<20} | {str(v.gender):<15} | {lang_str:<20}\n"
                f.write(line)
        print(f"Sucesso! {len(voices)} vozes salvas em voices_list.txt")
                
    except Exception as e:
        print(f"Erro ao listar vozes: {e}")

if __name__ == "__main__":
    list_all_voices()
