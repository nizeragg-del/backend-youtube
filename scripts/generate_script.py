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
    Você é um roteirista especializado em vídeos curtos (Shorts/Reels/TikTok) sobre o nicho: "{topic}".
    Sua tarefa é criar um roteiro cativante, um título viral e hashtags estratégicas.

    REGRAS CRÍTICAS:
    1. Escolha um sub-tema específico e curioso dentro do nicho "{topic}".
    2. NUNCA use os textos de exemplo abaixo na sua resposta. Substitua-os por conteúdo REAL.
    3. Sua resposta deve começar OBRIGATORIAMENTE com as tags abaixo, preenchidas com conteúdo REAL:
    [TITLE]
    (Escreva aqui o título real)

    [HASHTAGS]
    (Escreva aqui as hashtags reais)
    
    4. Siga com exatamente 8 cenas usando as tags:
    [SCENE TEXT]
    (Escreva aqui apenas a fala do locutor)

    [SCENE IMAGE]
    (Escreva aqui o prompt da imagem em INGLÊS)

    ESTILO: Narrativa rápida, curiosa e que retenha a atenção até o final.
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
        for attempt in range(40): 
            time.sleep(3)
            try:
                status_resp = requests.get(f"{MANUS_API_URL}/{task_id}", headers=headers)
                status_resp.raise_for_status()
                status_data = status_resp.json()
            except requests.exceptions.HTTPError as he:
                if he.response.status_code == 404:
                    print(f"[Manus AI] Aviso: 404 Not Found na tentativa {attempt+1}. Aguardando consistência da API...")
                    continue
                else:
                    raise he
            
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

                # Extração do TÍTULO e HASHTAGS (mais robusta com Regex)
                display_title = topic
                display_hashtags = "#shorts #viral #ai"
                
                # Extrai o título ignorando colchetes e instruções
                title_match = re.search(r"\[TITLE\]\s*(.*?)\s*(?:\[|$)", raw_text, re.DOTALL | re.IGNORECASE)
                if title_match:
                    title_raw = title_match.group(1).strip()
                    # Remove QUALQUER coisa entre parênteses, colchetes ou sinais de menor/maior (MULTILINE)
                    title_raw = re.sub(r'[\(\[<].*?[\)\]>]', '', title_raw, flags=re.DOTALL).strip()
                    # Filtra linhas de instrução
                    lines = [l.strip() for l in title_raw.split("\n") if l.strip()]
                    blacklisted = ["Título", "Instruções", "tag", "TEMA", "NICHO", "Aqui você", "Exemplo", "Escreva aqui"]
                    for line in lines:
                        if any(x.lower() in line.lower() for x in blacklisted):
                            continue
                        display_title = line
                        break
                    print(f"[Manus AI] Sub-tema extraído: {display_title}")

                # Extrai hashtags
                tags_match = re.search(r"\[HASHTAGS\]\s*(.*?)\s*(?:\[|$)", raw_text, re.DOTALL | re.IGNORECASE)
                if tags_match:
                    tags_raw = tags_match.group(1).strip()
                    # Remove QUALQUER coisa entre parênteses, colchetes ou sinais de menor/maior (MULTILINE)
                    tags_raw = re.sub(r'[\(\[<].*?[\)\]>]', '', tags_raw, flags=re.DOTALL).strip()
                    lines = [l.strip() for l in tags_raw.split("\n") if l.strip()]
                    for line in lines:
                        if any(x in line for x in ["hashtags virais", "Adicione uma tag"]):
                            continue
                        display_hashtags = line
                        break
                    print(f"[Manus AI] Hashtags extraídas: {display_hashtags}")

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
                        # Limpeza ultra profunda do texto da cena
                        t = t.replace('\\"', '"').replace("\\'", "'").strip()
                        # Remove QUALQUER coisa entre parênteses (), colchetes [] ou tags < > (MULTILINE)
                        t = re.sub(r'[\(\[<].*?[\)\]>]', '', t, flags=re.DOTALL)
                        # Remove frases de exemplo residuais
                        blacklisted_phrases = ["Fala do locutor", "frases curtas", "Texto que o locutor", "Escreva aqui", "Aqui você"]
                        for phrase in blacklisted_phrases:
                            t = t.replace(phrase, "")
                        
                        t = t.strip()
                        
                        if t and p:
                            final_text += t + " "
                            image_prompts.append(p.strip())
                    final_text = final_text.strip() # Ensure final_text is stripped after concatenation
                    print(f"[Manus AI] Roteiro extraído: {len(blocks)} cenas.") # Changed to blocks as scripts list is not used here
                
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
