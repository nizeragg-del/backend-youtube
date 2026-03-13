import os
import time
import requests # type: ignore
from dotenv import load_dotenv # type: ignore

# Carrega o .env
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_path, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

MANUS_API_URL = os.getenv("MANUS_API_URL", "https://api.manus.ai/v1/tasks")
MANUS_API_KEY = os.getenv("MANUS_API_KEY", "")

def generate_manus_image(prompt, index, output_dir):
    """
    Solicita a criação de uma imagem ao Manus AI e faz o download.
    """
    if not MANUS_API_KEY:
        print("[Manus AI Image] Erro: MANUS_API_KEY não configurada.")
        return None

    headers = {
        "API_KEY": MANUS_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Prompt formatado para garantir que o Manus AI saiba que deve GERAR uma imagem
    task_prompt = f"Generate a cinematic, high-quality image based on this description: {prompt}. Return only the direct URL of the generated image."
    
    data = {
        "prompt": task_prompt,
        "agentProfile": "manus-1.6" # Assumindo que o mesmo perfil lida com ferramentas de imagem
    }

    try:
        response = requests.post(MANUS_API_URL, headers=headers, json=data)
        response.raise_for_status()
        task_id = response.json().get("task_id")
        
        if not task_id:
            print(f"[Manus AI Image] Erro ao criar tarefa para imagem {index}.")
            return None

        print(f"[Manus AI Image] Tarefa {task_id} criada para imagem {index}. Aguardando...")
        
        # Polling
        for _ in range(60): # Até 3 minutos para geração de imagem
            time.sleep(5)
            status_resp = requests.get(f"{MANUS_API_URL}/{task_id}", headers=headers)
            status_resp.raise_for_status()
            status_data = status_resp.json()
            
            status = status_data.get("status") or status_data.get("task_status")
            if status in ["completed", "DONE"]:
                # Extração da URL (procura por padrões de URL na resposta)
                import re
                result_text = str(status_data.get("result", "") or status_data.get("output", ""))
                url_match = re.search(r'(https?://\S+\.(?:png|jpg|jpeg|webp|gif))', result_text, re.IGNORECASE)
                
                if url_match:
                    image_url = url_match.group(1)
                    print(f"[Manus AI Image] Imagem {index} gerada: {image_url}")
                    
                    # Download da imagem
                    img_resp = requests.get(image_url)
                    img_resp.raise_for_status()
                    
                    filename = f"scene_{index}.png"
                    local_path = os.path.join(output_dir, filename)
                    with open(local_path, "wb") as f:
                        f.write(img_resp.content)
                    
                    return f"assets/images/{filename}"
                else:
                    print(f"[Manus AI Image] Aviso: Tarefa concluída mas URL não encontrada no resultado: {result_text[:100]}...")
                    return None
            elif status in ["failed", "ERROR"]:
                print(f"[Manus AI Image] Falha na tarefa {task_id}: {status_data.get('message')}")
                return None
                
        print(f"[Manus AI Image] Timeout aguardando imagem {index}.")
        return None

    except Exception as e:
        print(f"[Manus AI Image] Erro inesperado: {e}")
        return None
