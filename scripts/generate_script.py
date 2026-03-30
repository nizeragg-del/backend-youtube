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

def generate_script(topic="tópico interessante", video_type="viral", image_references=None):
    """
    Solicita um roteiro ao Manus AI com base no tipo de vídeo e referências.
    """
    manus_key = get_manus_key()
    if not manus_key:
        print("[Manus AI] Erro: MANUS_API_KEY não configurada.")
        return None

    # Ajuste do tom com base no tipo
    if video_type == "creative":
        tone_instruction = "Foque em copywriting persuasivo, storytelling criativo e destaque as qualidades do produto."
        if image_references:
            tone_instruction += f" Considere as seguintes referências visuais em anexo: {', '.join(image_references)}."
    else:
        tone_instruction = "Foque em retenção máxima, hooks agressivos no início e conteúdo com alto potencial de compartilhamento (viralidade)."

    prompt = f"""
    Você é um roteirista especializado em vídeos curtos (Shorts/Reels/TikTok) estilo "{video_type}".
    Nicho: "{topic}".
    {tone_instruction}

    REGRAS CRÍTICAS:
    1. Escolha um sub-tema específico e curioso dentro do nicho "{topic}".
    2. NUNCA use os textos de exemplo abaixo na sua resposta. Substitua-os por conteúdo REAL.
    3. Sua resposta deve conter OBRIGATORIAMENTE os blocos:
    [TITLE] (Título curto e impactante, sem quebras de linha ou /n)
    [HASHTAGS] (Hashtags estratégicas)
    
    4. Siga com exatamente 8 cenas usando rigorosamente:
    [SCENE TEXT] (Apenas a fala do locutor. Remova qualquer \n, /n ou marcador extra.)
    [SCENE IMAGE] (Prompt da imagem em INGLÊS focado no conteúdo da cena)

    ESTILO: {'Elegante e Persuasivo' if video_type == 'creative' else 'Rápido e Curioso'}.
    IMPORTANTE: Não coloque nada além do conteúdo solicitado. Limpe o texto de qualquer resíduo técnico como '/n'.
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
        print(f"[Manus AI] Criando tarefa de roteirização ({video_type}) para: {topic}...")
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

                # Limpeza global de literal /n e \n no texto bruto recebido
                raw_text = raw_text.replace("/n", " ").replace("\\n", " ").replace("\n", " ").replace("\r", " ")

                # Extração do TÍTULO e HASHTAGS
                display_title = topic
                display_hashtags = "#shorts #viral #ai"
                
                title_match = re.search(r"\[TITLE\]\s*(.*?)\s*(?:\[|$)", raw_text, re.IGNORECASE)
                if title_match:
                    display_title = title_match.group(1).strip()
                    # Limpeza agressiva do título
                    display_title = re.sub(r'[\(\[<].*?[\)\]>]', '', display_title)
                    display_title = re.sub(r'\s+', ' ', display_title).strip()

                tags_match = re.search(r"\[HASHTAGS\]\s*(.*?)\s*(?:\[|$)", raw_text, re.IGNORECASE)
                if tags_match:
                    display_hashtags = tags_match.group(1).strip()
                    display_hashtags = re.sub(r'[\(\[<].*?[\)\]>]', '', display_hashtags)
                    display_hashtags = re.sub(r'\s+', ' ', display_hashtags).strip()

                final_text = ""
                image_prompts = []
                
                if isinstance(raw_text, (dict, list)):
                    raw_text = str(raw_text)
                
                # Regex para extrair cenas
                blocks = re.findall(r'\[SCENE TEXT\](.*?)(?:\[SCENE IMAGE\])(.*?)(?=\[SCENE TEXT\]|\Z)', raw_text, re.IGNORECASE)
                
                if blocks:
                    for t, p in blocks:
                        # Limpeza profunda do texto da cena
                        t = t.replace('\\"', '"').replace("\\'", "'").strip()
                        # Remove quebras de linha e /n
                        t = t.replace("/n", " ").replace("\\n", " ")
                        # Remove comentários entre colchetes/parênteses/tags
                        t = re.sub(r'[\(\[<].*?[\)\]>]', '', t)
                        # Remove espaços múltiplos
                        t = re.sub(r'\s+', ' ', t).strip()
                        
                        if t and p:
                            final_text += t + " "
                            image_prompts.append(p.strip())
                    final_text = final_text.strip()
                    print(f"[Manus AI] Roteiro extraído: {len(blocks)} cenas.")
                
                if not final_text or len(final_text) < 100:
                    print("[Manus AI] Falha ao extrair via Tags ou conteúdo insuficiente. Usando fallback...")
                    final_text = fallback_script()

                if not image_prompts:
                    image_prompts = [f"Cinematic scene about {display_title}"]

                return {
                    "title": display_title,
                    "hashtags": display_hashtags,
                    "text": final_text,
                    "image_prompts": image_prompts,
                    "type": video_type
                }
                
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
