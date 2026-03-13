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
    Crie um roteiro DETALHADO para um vídeo de YouTube Shorts com duração exata entre 50 e 60 segundos sobre o tema: {topic}.
    O nicho é Religioso/Espiritual. 
    
    INSTRUÇÕES CRITICAIS:
    - O roteiro (texto falado) deve ter entre 600 e 1000 caracteres.
    - O roteiro deve ser fluido, emocionante e profundo.
    - Retorne o texto que será falado dentro das tags <roteiro> e </roteiro>.
    - Retorne exatamente 10 prompts de imagem (um para cada "cena" ou momento do vídeo) dentro das tags <imagens> e </imagens>.
    - Cada prompt de imagem deve estar em uma nova linha, em INGLÊS, descrevendo uma cena cinematográfica, épica e espiritual baseada no roteiro.
    - Não inclua instruções de cena, nomes de personagens ou observações dentro das tags de roteiro.

    ESTRUTURA DO CONTEÚDO:
    - Uma introdução poderosa (HOOK).
    - Uma reflexão bíblica profunda e detalhada (DESENVOLVIMENTO).
    - Uma mensagem de esperança e fé impactante (CLÍMAX).
    - Call to action final: 'Deixe um amém nos comentários e compartilhe essa luz com quem você ama'.
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
                
                def extract_text(obj, visited=None):
                    if visited is None: visited = set()
                    if id(obj) in visited: return ""
                    visited.add(id(obj))

                    if not obj: return ""
                    if isinstance(obj, str): return obj.strip()
                    if isinstance(obj, list): 
                        return "\n".join([extract_text(i, visited) for i in obj if i])
                    
                    if isinstance(obj, dict):
                        # CHAVES PROIBIDAS - Nunca extrair texto de campos de entrada/config
                        keys_to_ignore = ["prompt", "agentProfile", "headers", "payload", "input", "task_id", "status", "created_at", "config"]
                        
                        # Tenta campos de saída conhecidos primeiro
                        for k in ["content", "output", "result", "text", "message", "answer"]:
                            if k in obj and obj[k] and k not in keys_to_ignore:
                                res = extract_text(obj[k], visited)
                                if res: return res
                        
                        # Se não achou nos campos óbvios, concatena o resto
                        parts = []
                        for k, v in obj.items():
                            if k not in keys_to_ignore:
                                part = extract_text(v, visited)
                                if part: parts.append(part)
                        return "\n".join(parts)
                    return "" 

                # Tenta extrair de várias fontes
                raw_text = extract_text(status_data)
                
                print(f"[Manus AI Debug] Tamanho do texto bruto extraído: {len(raw_text)}")
                if len(raw_text) > 0:
                    print(f"[Manus AI Debug] Primeiros 200 caracteres: {raw_text[:200]}...")

                # Extração Resiliente usando findall para pegar o ÚLTIMO (geralmente o output, não a instrução do prompt)
                scripts_found = re.findall(r"<roteiro>(.*?)</roteiro>", raw_text, re.DOTALL | re.IGNORECASE)
                images_found = re.findall(r"<imagens>(.*?)</imagens>", raw_text, re.DOTALL | re.IGNORECASE)
                
                extracted_text = ""
                image_prompts = []

                if scripts_found:
                    extracted_text = scripts_found[-1].strip() # Pega o último match
                    print(f"[Manus AI] Tag <roteiro> encontrada ({len(scripts_found)} ocorrências). Usando a última.")
                else:
                    print("[Manus AI] Aviso: Tag <roteiro> não encontrada. Usando texto bruto.")
                    extracted_text = raw_text

                if images_found:
                    raw_images_text = images_found[-1].strip()
                    raw_images = raw_images_text.split("\n")
                    image_prompts = [img.strip() for img in raw_images if img.strip() and len(img) > 10]
                    # Limpa números e prefixos (ex: "1. ", "2- ")
                    image_prompts = [re.sub(r'^\d+[\.\-\)]\s*', '', p) for p in image_prompts]
                    image_prompts = image_prompts[:10]
                    print(f"[Manus AI] Tag <imagens> encontrada: {len(image_prompts)} prompts extraídos.")
                else:
                    print("[Manus AI] Aviso: Tag <imagens> não encontrada.")

                # Limpeza do Roteiro - Simplificada para evitar deletar tudo
                lines = extracted_text.split("\n")
                cleaned_lines = []
                for line in lines:
                    l = line.strip()
                    if not l: continue
                    upper_l = l.upper()
                    
                    # Remove apenas linhas que são puramente tags ou avisos de instrução
                    skip_patterns = ["<ROTEIRO>", "</ROTEIRO>", "<IMAGENS>", "</IMAGENS>"]
                    if any(x == upper_l for x in skip_patterns):
                        continue
                    
                    l = l.replace("**", "").replace("#", "").strip()
                    cleaned_lines.append(str(l))
                
                final_text = "\n".join(cleaned_lines).strip()
                
                # Validação de Fallback
                if len(final_text) < 150 and not scripts_found:
                    print("[Manus AI] Roteiro muito curto e sem tags. Ativando fallback.")
                    final_text = fallback_script()

                print(f"[Manus AI] Roteiro finalizado com {len(final_text)} caracteres e {len(image_prompts)} prompts de imagem.")
                
                return {
                    "text": final_text.strip(),
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
