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
MANUS_API_URL = os.getenv("MANUS_API_URL", "https://api.manus.ai/v1/tasks")
# A chave deve ser lida dentro da função ou atualizada após o load_dotenv
def get_manus_key():
    return os.getenv("MANUS_API_KEY", "")

def generate_script(topic="história bíblica", max_duration_sec=50):
    """
    Solicita um roteiro ao Manus AI através do sistema de Tasks e aguarda o resultado.
    """
    manus_key = get_manus_key()
    if not manus_key:
        print("[Manus AI] Erro: MANUS_API_KEY não configurada.")
        return None

    prompt = f"""
    Crie um roteiro DETALHADO para um vídeo de YouTube Shorts com duração exata entre 45 e 55 segundos sobre o tema: {topic}.
    O nicho é Religioso/Espiritual. 
    
    INSTRUÇÕES CRITICAIS E OBRIGATÓRIAS:
    - VOCÊ DEVE RESPONDER EXCLUSIVAMENTE COM UM CÓDIGO JSON VÁLIDO. 
    - O JSON deve conter apenas uma chave principal chamada "scenes", contendo uma lista com exatamente 10 objetos.
    - Cada objeto da lista "scenes" deve ter:
      * "text": A fala exata do locutor daquela cena (1 ou 2 frases fluídas, sem numeração).
      * "image_prompt": O prompt da imagem para aquela cena, escrito em INGLÊS, descrevendo uma cena cinematográfica, épica e espiritual.
    - PROIBIDO: Não inclua "Roteiro final:", cumprimentos, ou formato markdown fora do JSON.
    - PROIBIDO: NÃO crie arquivos (como .json, .txt, etc) para anexar. Você DEVE imprimir/retornar o JSON inteiro diretamente na sua resposta de texto.
    - SEJA CURTO E DIRETO: A soma do campo "text" de todas as cenas juntas não deve passar de 650 caracteres. O "image_prompt" deve ser uma frase curta de no máximo 15 palavras.
    
    ESTRUTURA DO CONTEÚDO:
    - Cena 1 a 2: Hook poderoso.
    - Cena 3 a 8: Reflexão profunda.
    - Cena 9 a 10: Clímax e Call to Action ('Deixe um amém nos comentários e compartilhe essa luz com quem você ama.').
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
            status_resp = requests.get(f"https://api.manus.ai/v1/tasks/{task_id}", headers=headers)
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

                # 1. Tenta extrair individualmente com Regex (imune a cortes ou JSONs incompletos ou markdown quebrado)
                # Formato esperado: "text": "...", "image_prompt": "..." dentro de chaves. Usaremos um findall direto nas chaves.
                # Ele pega o conteúdo de "text" e "image_prompt" linha a linha.
                
                final_text = ""
                image_prompts = []
                
                # Busca robusta que não exige que o JSON pareça estar fechado na ponta
                # Encontra qualquer bloco com formato "text": "X", "image_prompt": "Y"
                blocks = re.findall(r'"text"\s*:\s*"(.*?)",\s*"image_prompt"\s*:\s*"(.*?)"', raw_text, re.DOTALL | re.IGNORECASE)
                
                # Se não achou na ordem exata, tenta a ordem invertida só para garantir
                if not blocks:
                    blocks_inv = re.findall(r'"image_prompt"\s*:\s*"(.*?)",\s*"text"\s*:\s*"(.*?)"', raw_text, re.DOTALL | re.IGNORECASE)
                    blocks = [(t, p) for p, t in blocks_inv]
                
                if blocks:
                    for t, p in blocks:
                        # Limpeza básica em caso de escaped quotes internas
                        clean_t = t.replace('\\"', '"').strip()
                        clean_p = p.replace('\\"', '"').strip()
                        # Não adiciona se tiver lixo residual
                        if len(clean_t) > 5 and len(clean_p) > 5:
                            scripts.append(clean_t)
                            image_prompts.append(clean_p)
                            
                    if scripts:
                        final_text = " ".join(scripts).strip()
                        print(f"[Manus AI] JSON fragmentado/parcial lido via Regex! {len(scripts)} cenas extraídas perfeitamente mesmo com possível corte.")
                
                # Se ainda sim falhar completamente, volta à tentativa de JSON inteiro:
                if not final_text:
                    match = re.search(r'(\{.*"scenes".*\})', raw_text, re.DOTALL | re.IGNORECASE)
                    if match:
                        json_str = match.group(1)
                        try:
                            parsed = json.loads(json_str)
                            scenes = parsed.get("scenes", [])
                            
                            for s in scenes:
                                scripts.append(s.get("text", "").strip())
                                image_prompts.append(s.get("image_prompt", "").strip())
                                
                            final_text = " ".join(scripts).strip()
                            print(f"[Manus AI] JSON textualmente parseado com sucesso! {len(scenes)} cenas extraídas.")
                            
                        except json.JSONDecodeError as e:
                            print(f"[Manus AI] Erro no parser do JSON: {e}")
                

                # Se não extraiu nada textualmente, tenta procurar se a IA gerou um ARQUIVO .json e baixar
                if not final_text:
                    def find_json_url(obj):
                        if isinstance(obj, str):
                            m = re.search(r'(https?://\S+\.json)', obj, re.IGNORECASE)
                            return m.group(1) if m else None
                        if isinstance(obj, list):
                            for item in obj:
                                url = find_json_url(item)
                                if url: return url
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                url = find_json_url(v)
                                if url: return url
                        return None

                    file_url = find_json_url(status_data)
                    if file_url:
                        print(f"[Manus AI] Detectado arquivo anexo. Baixando JSON gerado em: {file_url}")
                        try:
                            file_resp = requests.get(file_url, timeout=30)
                            file_resp.raise_for_status()
                            parsed = file_resp.json()
                            scenes = parsed.get("scenes", [])
                            
                            scripts = []
                            for s in scenes:
                                scripts.append(s.get("text", "").strip())
                                image_prompts.append(s.get("image_prompt", "").strip())
                                
                            final_text = " ".join(scripts).strip()
                            print(f"[Manus AI] Arquivo JSON baixado e parseado! {len(scenes)} cenas extraídas.")
                        except Exception as e:
                            print(f"[Manus AI] Erro ao baixar ou ler o arquivo JSON anexo: {e}")

                if not final_text:
                    print("[Manus AI] Falha ao extrair via JSON ou anexo. Tentando fallback heurístico...")
                    final_text = fallback_script()
                
                # Validação Crítica
                if len(final_text) < 150:
                    print(f"[Manus AI] Roteiro final ({len(final_text)} chars) muito curto. Ativando fallback...")
                    final_text = fallback_script()
                
                if not image_prompts:
                    print("[Manus AI] Sem prompts de imagem detectados. Gerando lista básica...")
                    image_prompts = ["Cinematic scene about faith", "Epic biblical landscape", "Spiritual light and peace"]

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
        "Se você parou nesse vídeo, Deus tem um recado urgente para você.\n"
        "Muitas vezes a tempestade parece grande demais e as forças parecem acabar.\n"
        "Mas lembre-se de que a calmaria sempre vem após os ventos mais fortes.\n"
        "Deus está abrindo uma porta gigantesca na sua vida financeira e espiritual.\n"
        "Receba essa graça agora mesmo.\n"
        "Se essa palavra te acalmou, compartilhe com quem precisa e deixe um amém nos comentários."
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
