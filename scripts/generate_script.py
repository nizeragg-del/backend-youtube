import os
import json
import requests # type: ignore
from dotenv import load_dotenv # type: ignore

# Carrega o .env da raiz do projeto, independente de onde o script é chamado
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_path, ".env")
env_example_path = os.path.join(base_path, ".env.example")

if os.path.exists(env_path):
    load_dotenv(env_path)
elif os.path.exists(env_example_path):
    load_dotenv(env_example_path)
else:
    load_dotenv()

# Configurações Manus AI
MANUS_API_URL = os.getenv("MANUS_API_URL", "https://api.manus.im/v1/tasks")
# A chave deve ser lida dentro da função ou atualizada após o load_dotenv
def get_manus_key():
    return os.getenv("MANUS_API_KEY", "")

def generate_script(topic="tópico interessante", max_duration_sec=50):
    """
    Solicita um roteiro ao Manus AI através do sistema de Tasks e aguarda o resultado.
    """
    manus_key = get_manus_key()
    if not manus_key:
        print("[Manus AI] Erro: MANUS_API_KEY não configurada.")
        return None

    prompt = f"""
    Você é um roteirista especializado em vídeos virais de YouTube Shorts.
    TEMA/NICHO RECEBIDO: {topic}
    
    SUA MISSÃO:
    1. A partir deste NICHO, escolha um sub-tópico específico, curioso e impactante. 
       Exemplo: Se o nicho for "Histórias Bíblicas", escolha "A Coragem de Davi" ou "O Mistério de Melquisedeque".
    2. Crie um roteiro DETALHADO para um vídeo de 45 a 55 segundos.
    
    INSTRUÇÕES OBRIGATÓRIAS:
    - Comece sua resposta EXATAMENTE com a tag do título: [TITLE] <Título Curto e Viral>
    - Adicione uma tag para as hashtags sugeridas: [HASHTAGS] <3 a 5 hashtags virais separadas por espaço>
    - Siga com exatamente 8 cenas usando as tags:
      [SCENE TEXT] <Fala do locutor (máximo 2 frases curtas)>
      [SCENE IMAGE] <Prompt detalhado da imagem em INGLÊS>
    
    REGRAS DE OURO:
    - PROIBIDO repetir instruções ou adicionar introduções. Comece direto com [TITLE].
    - O texto total das falas não deve ultrapassar 500 caracteres.
    - Seja criativo e varie o tema e as hashtags dentro do nicho a cada solicitação.
    """
    
    headers = {
        "API_KEY": manus_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": prompt,
        "agentProfile": "manus-1.6" 
    }

    try:
        print(f"[Manus AI] Criando tarefa de roteirização para o nicho: {topic}...")
        response = requests.post(MANUS_API_URL, headers=headers, json=data)
        response.raise_for_status()
        task_data = response.json()
        
        task_id = task_data.get("task_id")
        if not task_id:
            print("[Manus AI] Erro: task_id não recebido.")
            return None

        print(f"[Manus AI] Tarefa {task_id} criada. Aguardando conclusão...")
        import time
        import re
        for _ in range(40): 
            time.sleep(3)
            status_resp = requests.get(f"{MANUS_API_URL}/{task_id}", headers=headers)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            
            status = status_data.get("status") or status_data.get("task_status")
            if status == "completed" or status == "DONE":
                print("[Manus AI] Roteiro e prompts de imagem gerados!")
                
                # Tenta extrair a string completa do JSON
                raw_text = status_data.get("output")
                if not raw_text:
                    if "result" in status_data: 
                        raw_text = status_data["result"]
                    else:
                        def scrape_all_text(d):
                            if isinstance(d, dict):
                                return " ".join(scrape_all_text(v) for k, v in d.items() if k not in ['prompt', 'input', 'task_id'])
                            elif isinstance(d, list):
                                return " ".join(scrape_all_text(x) for x in d)
                            elif isinstance(d, str):
                                return d
                            return ""
                        raw_text = scrape_all_text(status_data)

                if not isinstance(raw_text, str):
                    try:
                        raw_text = json.dumps(raw_text, ensure_ascii=False)
                    except:
                        raw_text = str(raw_text)

                # Extração do TÍTULO e HASHTAGS
                display_title = topic
                display_hashtags = "#shorts #viral #ai"
                
                if "[TITLE]" in raw_text:
                    try:
                        title_part = raw_text.split("[TITLE]")[1].split("[HASHTAGS]")[0].split("[SCENE TEXT]")[0].strip()
                        if title_part:
                            display_title = title_part
                            print(f"[Manus AI] Sub-tema escolhido: {display_title}")
                    except: pass
                
                if "[HASHTAGS]" in raw_text:
                    try:
                        hashtags_part = raw_text.split("[HASHTAGS]")[1].split("[SCENE TEXT]")[0].strip()
                        if hashtags_part:
                            display_hashtags = hashtags_part
                            print(f"[Manus AI] Hashtags sugeridas: {display_hashtags}")
                    except: pass

                final_text = ""
                image_prompts = []
                scripts = []
                
                # Desfaz qualquer possível layer de cast string
                if isinstance(raw_text, dict) or isinstance(raw_text, list):
                    raw_text = str(raw_text)
                
                # Regex para extrair cenas
                blocks = re.findall(r'\[SCENE TEXT\](.*?)(?:\[SCENE IMAGE\])(.*?)(?=\[SCENE TEXT\]|\Z)', raw_text, re.DOTALL | re.IGNORECASE)
                
                if blocks:
                    for t, p in blocks:
                        t = t.replace('\\"', '"').replace("\\'", "'").strip()
                        p = p.replace('\\"', '"').replace("\\'", "'").strip()
                        if len(t) > 5 and len(p) > 5:
                            scripts.append(t)
                            image_prompts.append(p)
                    final_text = " ".join(scripts).strip()
                    print(f"[Manus AI] Roteiro extraído: {len(scripts)} cenas.")
                
                if not final_text:
                    print("[Manus AI] Falha ao extrair via Tags. Usando fallback...")
                    final_text = fallback_script()

                if len(final_text) < 150:
                    final_text = fallback_script()
                
                if not image_prompts:
                    image_prompts = [f"Cinematic scene about {display_title}", f"Epic landscape of {display_title}"]

                return {
                    "title": display_title,
                    "hashtags": display_hashtags,
                    "text": final_text,
                    "image_prompts": image_prompts
                }
            elif status == "failed" or status == "ERROR":
                print(f"[Manus AI] Falha na tarefa: {status_data.get('error') or status_data.get('message')}")
                return None
            
        print("[Manus AI] Timeout aguardando a tarefa.")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"[!] Erro HTTP ao chamar Manus AI: {e}")
        if e.response is not None:
            print(f"    Status Code: {e.response.status_code}")
            print(f"    Resposta: {e.response.text}")
        return None
    except Exception as e:
        print(f"[!] Erro inesperado ao chamar Manus AI: {e}")
        return None

def fallback_script():
    return (
        "O mundo está cheio de curiosidades fascinantes que muitas vezes ignoramos.\n"
        "Desde o fundo dos oceanos até as galáxias mais distantes, a ciência nos surpreende.\n"
        "Cada pequena descoberta nos mostra o quanto ainda temos a aprender sobre a natureza.\n"
        "Se você gosta de aprender algo novo todos os dias, este canal é para você.\n"
        "Acompanhe nossos vídeos diários e expanda seus horizontes.\n"
        "Se essa curiosidade te surpreendeu, curta e compartilhe com um amigo."
    )

if __name__ == "__main__":
    script = generate_script("oração poderosa para acalmar a ansiedade")
    if script:
        print("\n--- ROTEIRO GERADO ---")
        print(script)
        
        # Salva o roteiro na pasta de assets/ para debug
        output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "script.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(str(script))
        print(f"\nRoteiro salvo em: {output_path}")
    else:
        print("\n[!] Falha ao gerar roteiro na execução direta.")
