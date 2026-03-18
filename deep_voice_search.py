import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TYPECAST_API_KEY")

def deep_search():
    print("Iniciando busca profunda por vozes em Português...")
    url = "https://api.typecast.ai/v1/actors"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erro: {response.status_code} - {response.text}")
        return

    data = response.json()
    voices = data.get("voices", [])
    print(f"Total de vozes no catálogo: {len(voices)}")
    
    results = []
    keywords = ["Portuguese", "Português", "Brazil", "Brasil", "pt-BR", "pt-PT", "pt_BR", "pt_PT"]
    
    for v in voices:
        v_str = json.dumps(v, ensure_ascii=False).lower()
        found = any(k.lower() in v_str for k in keywords)
        
        if found:
            results.append({
                "id": v.get("actor_id"),
                "name": v.get("name"),
                "desc": v.get("description"),
                "tags": v.get("tags", []),
                "gender": v.get("gender")
            })
            
    if results:
        print(f"\nEncontradas {len(results)} vozes com palavras-chave:")
        for r in results:
            print(f"- {r['name']} ({r['id']}): {r['desc']} | Tags: {r['tags']}")
    else:
        print("\nNenhuma voz encontrada com as palavras-chave explícitas.")
        
    # Busca por nomes comuns brasileiros
    brazilian_names = ["Ricardo", "Fernanda", "Gabriel", "Lúcia", "Felipe", "Antônio", "Maria", "João", "Ana", "Luiz"]
    print("\nBuscando por nomes brasileiros comuns...")
    name_results = []
    for v in voices:
        name = v.get("name", "")
        if name in brazilian_names:
            name_results.append(v)
            
    if name_results:
        print(f"Encontradas {len(name_results)} vozes com nomes brasileiros:")
        for r in name_results:
            print(f"- {r.get('name')} ({r.get('actor_id')})")
    else:
        print("Nenhuma voz encontrada com nomes brasileiros comuns.")

if __name__ == "__main__":
    deep_search()
