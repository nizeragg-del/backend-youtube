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
    Crie um roteiro DETALHADO para um vídeo de YouTube Shorts com duração exata entre 45 e 55 segundos sobre o tema: {topic}.
    O nicho deve ser adaptado exatamente ao tema solicitado. 
    
    INSTRUÇÕES CRITICAIS E OBRIGATÓRIAS:
    - VOCÊ ESTÁ PROIBIDO DE USAR JSON OU ARQUIVOS. RESPONDA DIRETAMENTE NO TEXTO.
    - Siga RIGOROSAMENTE as tags exatas abaixo para CADA UMA das 8 cenas (MÁXIMO 8 CENAS PARA NÃO PASSAR DE 60 SEGUNDOS):
    [SCENE TEXT] <insira aqui a fala do locutor>
    [SCENE IMAGE] <insira aqui o prompt em inglês>

    - IMPORTANTE: NÃO repita o texto "A fala exata do locutor" nem "Roteiro final" na sua resposta. Comece direto no conteúdo.
    - SEJA CURTO E DIRETO: A regra de tamanho é rígida. Não ultrapasse 500 caracteres somando todas as falas das 8 cenas.
    - PROIBIDO: Não adicione conclusões finais ou metadados da IA fora destas tags.
    
    
    ESTRUTURA DO CONTEÚDO (EXATAMENTE 8 CENAS):
    - Cena 1: Hook impactante.
    - Cena 2 a 7: Curiosidades ou história.
    - Cena 8: Call to Action final.
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
        print(f"[Manus AI] Criando tarefa de roteirização para: {topic}...")
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
                
                import json
                
                # ------ DEBUG PROFUNDO ------
                try:
                    debug_path = os.path.join(os.path.dirname(__file__), "..", "assets", "debug_manus_script.json")
                    with open(debug_path, "w", encoding="utf-8") as df:
                        json.dump(status_data, df, ensure_ascii=False, indent=2)
                    print(f"[Manus AI Debug] Payload completo da resposta salvo em: {debug_path}")
                except Exception as e:
                    print(f"[Manus AI Debug] Erro ao salvar payload: {e}")
                
                # Imprime chaves principais para log rápido no console
                print(f"[Manus AI Debug] Chaves presentes no JSON de resposta: {list(status_data.keys())}")
                # -----------------------------
                
                # Tenta extrair a string completa do JSON a partir dos dados retornados
                # Como solicitamos exclusivamente JSON, podemos tentar pegar o output e fazer dumps/loads
                # ou usar regex para localizar as chaves
                
                # Tentar achar output cru que seria a resposta textual da IA
                raw_text = status_data.get("output")
                if not raw_text:
                    if "result" in status_data: 
                        raw_text = status_data["result"]
                    else:
                        # Extração de segurança em todos os campos recursivamente se não vier nas chaves padrões
                        def scrape_all_text(d):
                            if isinstance(d, dict):
                                return " ".join(scrape_all_text(v) for k, v in d.items() if k not in ['prompt', 'input', 'task_id'])
                            elif isinstance(d, list):
                                return " ".join(scrape_all_text(x) for x in d)
                            elif isinstance(d, str):
                                return d
                            return ""
                        raw_text = scrape_all_text(status_data)

                # Garante que raw_text seja uma string com aspas duplas de JSON
                if not isinstance(raw_text, str):
                    try:
                        raw_text = json.dumps(raw_text, ensure_ascii=False)
                    except Exception:
                        raw_text = str(raw_text)

                final_text = ""
                image_prompts = []
                
                # O regex caça tudo que estiver entre [SCENE TEXT] e [SCENE IMAGE] (ou até a próxima SCENE TEXT / fim do texto)
                import re
                
                # Desfaz qualquer possível layer pesada de cast string
                if isinstance(raw_text, dict) or isinstance(raw_text, list):
                    raw_text = str(raw_text)
                
                # Primeiro tentamos quebrar por [SCENE TEXT]
                parts = raw_text.split("[SCENE TEXT]")
                scripts = []
                
                for part in parts[1:]: # O índice 0 é lixo prévio
                    # Cada part começa com a fala, seguida por [SCENE IMAGE] e pelo prompt
                    if "[SCENE IMAGE]" in part:
                        subparts = part.split("[SCENE IMAGE]")
                        t = subparts[0].strip()
                        # Limpa qualquer escape residual
                        t = t.replace('\\"', '"').replace("\\'", "'").replace('\\n', ' ')
                        
                        # FILTRAGEM DE BOILERPLATE (Se a IA for tonta e repetir minhas instruções)
                        blacklist = [
                            "A fala exata do locutor", 
                            "Roteiro final", 
                            "1 ou 2 frases curtas",
                            "insira aqui", 
                            "Prompt da imagem",
                            "(717 caracteres)"
                        ]
                        
                        is_junk = False
                        for junk in blacklist:
                            if junk.lower() in t.lower():
                                is_junk = True
                                break
                        
                        if is_junk:
                            continue

                        # O prompt de imagem vai até a próxima tag de SCENE TEXT (que já foi limado pelo split principal)
                        # Entao ele é o resto ou até "\n[" se houver lixo
                        p = subparts[1].split("\n[")[0].strip()
                        p = p.replace('\\"', '"').replace("\\'", "'").replace('\\n', ' ')
                        
                        if len(t) > 5 and len(p) > 5:
                            scripts.append(t)
                            image_prompts.append(p)
                
                if scripts:
                    final_text = " ".join(scripts).strip()
                    print(f"[Manus AI] Texto Tagueado extraído com sucesso! {len(scripts)} cenas processadas.")
                else:
                    # Fallback caso a IA use tags levemente diferentes
                    blocks = re.findall(r'\[SCENE TEXT\](.*?)(?:\[SCENE IMAGE\])(.*?)(?=\[SCENE TEXT\]|\Z)', raw_text, re.DOTALL | re.IGNORECASE)
                    if blocks:
                        for t, p in blocks:
                            t = t.replace('\\"', '"').replace("\\'", "'").strip()
                            p = p.replace('\\"', '"').replace("\\'", "'").strip()
                            if len(t) > 5 and len(p) > 5:
                                scripts.append(t)
                                image_prompts.append(p)
                        final_text = " ".join(scripts).strip()
                        print(f"[Manus AI] Texto Tagueado (Regex Fallback) extraído: {len(scripts)} cenas.")

                if not final_text:
                    print("[Manus AI] Falha ao extrair via Tags. O payload parecia não ter as tags corretas. Tentando fallback heurístico...")
                    print(f"--- DUMP BRUTO PARA DEBUG (Primeiros 1000 char) ---\n{raw_text[:1000]}\n--------------------------------")
                    final_text = fallback_script()

                
                # Validação Crítica
                if len(final_text) < 150:
                    print(f"[Manus AI] Roteiro final ({len(final_text)} chars) muito curto. Ativando fallback...")
                    final_text = fallback_script()
                
                if not image_prompts:
                    print("[Manus AI] Sem prompts de imagem detectados. Gerando lista básica...")
                    image_prompts = [f"Cinematic scene about {topic}", f"Epic landscape of {topic}", f"Vivid visual representation of {topic}"]

                return {
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
