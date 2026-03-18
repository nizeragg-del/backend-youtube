import os
import json
import requests # type: ignore
import time
import subprocess
from dotenv import load_dotenv # type: ignore

# Carrega o .env da raiz do projeto
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_path, ".env")
env_example_path = os.path.join(base_path, ".env.example")

if os.path.exists(env_path):
    load_dotenv(env_path)
elif os.path.exists(env_example_path):
    load_dotenv(env_example_path)
else:
    load_dotenv()

def get_typecast_keys():
    return {
        "key": os.getenv("TYPECAST_API_KEY", ""),
        "actor": os.getenv("TYPECAST_ACTOR_ID", "60b52a14c1143c4c95a23056")
    }

def get_audio_duration(file_path):
    """Retorna a duração do áudio em segundos usando ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"[!] Erro ao obter duração do áudio: {e}")
        return None

def transcribe_audio(audio_path):
    """Tenta transcrever o áudio usando o helper do Remotion se disponível."""
    try:
        # Tenta usar o script de transcrição do remotion (se configurado)
        # Por enquanto, fallback para o mock se não houver transcritor externo
        return None
    except Exception as e:
        print(f"[Whisper] Erro na transcrição: {e}")
        return None

def generate_voice(text, output_dir, speech_speed=1.0):
    """
    Envia o texto para a API do Typecast para gerar o áudio e cria sincronização.
    """
    keys = get_typecast_keys()
    typecast_key = keys["key"]
    typecast_actor = keys["actor"]
    
    audio_path = os.path.join(output_dir, "speech.mp3")
    sync_path = os.path.join(output_dir, "sync.json")
    
    headers = {
        "X-API-KEY": typecast_key,
        "Content-Type": "application/json"
    }
    
    if not typecast_key:
        print("[Typecast AI] Chave não encontrada. Usando modo MOCK...")
        return mock_generate_voice(text, audio_path, sync_path)

    try:
        print(f"[Typecast AI] Gerando voz ({typecast_actor})...")
        payload = {
            "voice_id": typecast_actor,
            "text": text,
            "model": "ssfm-v21"
        }
        
        response = requests.post("https://api.typecast.ai/v1/text-to-speech", headers=headers, json=payload)
        response.raise_for_status()
        
        with open(audio_path, "wb") as f:
            f.write(response.content)
            
        if speech_speed != 1.0:
            print(f"[Typecast AI] Ajustando velocidade do áudio para {speech_speed}x...")
            temp_audio = audio_path.replace(".mp3", "_temp.mp3")
            os.rename(audio_path, temp_audio)
            cmd = ["ffmpeg", "-y", "-i", temp_audio, "-filter:a", f"atempo={speech_speed}", "-vn", audio_path]
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                os.remove(temp_audio)
            except Exception as e:
                print(f"[!] Erro ao ajustar velocidade: {e}. Mantendo velocidade original.")
                if os.path.exists(temp_audio) and not os.path.exists(audio_path):
                    os.rename(temp_audio, audio_path)
            
        print("[Typecast AI] Áudio gerado. Sincronizando...")
        
        # Tenta a transcrição real
        return mock_generate_voice(text, audio_path, sync_path)
        
    except requests.exceptions.HTTPError as e:
        print(f"[!] Erro HTTP no Typecast AI: {e}")
        if e.response is not None:
            print(f"    Status: {e.response.status_code}")
            print(f"    Body: {e.response.text}")
        return None, None
    except Exception as e:
        print(f"[!] Erro inesperado no Typecast AI: {e}")
        return None, None

def mock_generate_voice(text, audio_path, sync_path):
    """
    Gera um mock json de sincronização de palavras.
    Normaliza os tempos para bater com a duração real do áudio se disponível.
    """
    words = text.split()
    if not words: return audio_path, sync_path
    
    # 1. Geração preliminar baseada em estimativa (V10 Elite Sync)
    temp_sync = []
    current_time = 0.0
    for w in words:
        clean_word = w.strip()
        if not clean_word: continue
        
        # Palavras maiores ganham mais peso, mas com um piso mínimo de 0.15s
        duration = float(0.15 + (len(clean_word) * 0.045)) # type: ignore
        temp_sync.append({
            "word": clean_word,
            "start": round(float(current_time), ndigits=3), # type: ignore
            "end": round(float(current_time + duration), ndigits=3) # type: ignore
        })
        current_time += duration + 0.015 # Pequeno respiro entre palavras

    # 2. Se o áudio real já existir, normalizamos os tempos
    if os.path.exists(audio_path):
        actual_duration = float(get_audio_duration(audio_path) or 0)
        if actual_duration > 0:
            estimated_duration = float(temp_sync[-1]["end"])
            ratio = float(actual_duration / estimated_duration)
            
            for item in temp_sync:
                item["start"] = round(float(item["start"]) * ratio, ndigits=3) # type: ignore
                item["end"] = round(float(item["end"]) * ratio, ndigits=3) # type: ignore
                # Garantia de que end > start após arredondamento
                if item["end"] <= item["start"]:
                    item["end"] = round(float(item["start"]) + 0.1, ndigits=3) # type: ignore
            
            print(f"[Typecast AI] Sincronia normalizada: Estimado {estimated_duration:.2f}s -> Real {actual_duration:.2f}s")
    else:
        # Salvar um arquivo de audio válido (WAV silêncio mínimo) se estiver em modo puro mock
        # WAV header de 44 bytes para um arquivo de silêncio
        wav_header = b'RIFF\x2c\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x80\x3e\x00\x00\x02\x00\x10\x00data\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        with open(audio_path, 'wb') as f:
            f.write(wav_header)

    with open(sync_path, "w", encoding="utf-8") as f:
        json.dump(temp_sync, f, indent=2, ensure_ascii=False)
        
    print(f"[Typecast AI] Áudio e Sync salvos em: {os.path.dirname(audio_path)}")
    return audio_path, sync_path

if __name__ == "__main__":
    test_text = "Se você está vendo isso agora, não é por acaso."
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    generate_voice(test_text, out_dir)
