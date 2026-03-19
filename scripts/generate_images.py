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

def get_manus_key():
    return os.getenv("MANUS_API_KEY", "")

def generate_manus_image(prompt, index, output_dir):
    """
    Solicita a criação de uma imagem ao Manus AI e faz o download.
    """
    manus_key = get_manus_key()
    if not manus_key:
        print("[Manus AI Image] Erro: MANUS_API_KEY não configurada.")
        return None

    headers = {
        "API_KEY": manus_key,
        "Content-Type": "application/json"
    }
    
    # Prompt formatado para garantir que o Manus AI saiba que deve GERAR uma imagem vertical
    task_prompt = f"Generate a cinematic, high-quality VERTICAL image (9:16 aspect ratio, portrait orientation) suitable for YouTube Shorts, based on this description: {prompt}. You must ensure it is 9:16 vertical ratio. Return only the direct URL of the generated image."
    
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

        print(f"[Manus AI Image] Tarefa {task_id} criada para imagem {index}. URL de polling: {MANUS_API_URL}/{task_id}")
        
        # Polling
        for attempt in range(60): # Até 3 minutos para geração de imagem
            time.sleep(5)
            try:
                status_resp = requests.get(f"{MANUS_API_URL}/{task_id}", headers=headers)
                status_resp.raise_for_status()
                status_data = status_resp.json()
            except requests.exceptions.HTTPError as he:
                if he.response.status_code == 404:
                    print(f"[Manus AI Image] Aviso: 404 Not Found na tentativa {attempt+1}. Aguardando consistência da API...")
                    continue
                else:
                    raise he
            
            status = status_data.get("status") or status_data.get("task_status")
            if status in ["completed", "DONE"]:
                # Extração Robusta de URL (procura recursiva)
                def find_image_url(obj):
                    if isinstance(obj, str):
                        import re
                        match = re.search(r'(https?://\S+\.(?:png|jpg|jpeg|webp|gif))', obj, re.IGNORECASE)
                        return match.group(1) if match else None
                    if isinstance(obj, list):
                        for item in obj:
                            url = find_image_url(item)
                            if url: return url
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k not in ["prompt", "agentProfile"]: # Ignora campos de entrada
                                url = find_image_url(v)
                                if url: return url
                    return None

                image_url = find_image_url(status_data)
                
                if image_url:
                    print(f"[Manus AI Image] Imagem {index} gerada: {image_url}")
                    
                    # Download da imagem
                    try:
                        img_headers = {}
                        if "manuscdn.com" in image_url:
                            img_headers["API_KEY"] = manus_key
                            
                        img_resp = requests.get(image_url, headers=img_headers, timeout=30)
                        img_resp.raise_for_status()
                        
                        filename = f"scene_{index}.png"
                        local_path = os.path.join(output_dir, filename)
                        with open(local_path, "wb") as f:
                            f.write(img_resp.content)
                        
                        return f"assets/images/{filename}"
                    except Exception as e:
                        print(f"[Manus AI Image] Erro ao baixar imagem {index}: {e}")
                        return None
                else:
                    print(f"[Manus AI Image] Aviso: Tarefa concluída mas URL não encontrada no resultado.")
                    # Log resumido do resultado para debug se falhar
                    debug_str = str(status_data)[:500]
                    print(f"[Manus AI Image Debug] Resumo do resultado: {debug_str}...")
                    return None
            elif status in ["failed", "ERROR"]:
                print(f"[Manus AI Image] Falha na tarefa {task_id}: {status_data.get('message')}")
                return None
                
        print(f"[Manus AI Image] Timeout aguardando imagem {index}.")
        return None

    except Exception as e:
        print(f"[Manus AI Image] Erro inesperado: {e}")
        return None
