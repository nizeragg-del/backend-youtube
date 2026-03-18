import os
import re
import time
import shutil
from dotenv import load_dotenv
from pydub import AudioSegment
from typecast import Typecast
from typecast.models import TTSRequest, TTSModel, Prompt

load_dotenv()

# Configuração manual do FFmpeg caso não esteja no PATH
FFMPEG_BIN_PATH = r"C:\Users\ctb075\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(FFMPEG_BIN_PATH):
    # Adicionamos ao PATH do sistema para esta execução
    if FFMPEG_BIN_PATH not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + FFMPEG_BIN_PATH
    AudioSegment.converter = os.path.join(FFMPEG_BIN_PATH, "ffmpeg.exe")
    AudioSegment.ffprobe = os.path.join(FFMPEG_BIN_PATH, "ffprobe.exe")

# VOZ PADRÃO (Camila - pt-BR)
# Nota: Esta voz usa o modelo SSFM_V21.
DEFAULT_VOICE_ID = "tc_5f8d7b0de146f10007b8042f"

def _clean_narration_text(text: str) -> str:
    """
    Remove cabeçalhos estruturais, tempos e rótulos que não devem ser narrados.
    Exemplos: "1. Hook poderoso (5-10s)", "Cena 1: ", "[00:10]", "(10s)", etc.
    """
    if not text:
        return ""
    
    # 1. Remover listas numeradas com rótulos (ex: "1. Hook poderoso", "2. Reflexão")
    # Padrão: número + ponto + espaço + Palavra sugerindo estrutura + opcionalmente tempo
    text = re.sub(r'^\d+\.\s*(Hook|Reflexão|Clímax|Introdução|Desfecho|CTA|Cena|Scene|Início|Fim|Ponte)[^:]*[:\s-]*', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # 2. Remover marcações de tempo entre parênteses ou colchetes (ex: "(5-10s)", "[30s]", "(10-15 segundos)")
    text = re.sub(r'[\(\[][\d\-\s]*(s|seg|segundos|seconds)[\)\]]', '', text, flags=re.IGNORECASE)
    
    # 3. Remover rótulos explícitos de cena ou partes (ex: "Cena 1:", "Scene 10 -", "Parte 2:")
    text = re.sub(r'(Cena|Scene|Parte|Part)\s*\d+[:\s-]*', '', text, flags=re.IGNORECASE)
    
    # 4. Remover prefixos de narração (ex: "Narração:", "Texto:", "Narrador:")
    text = re.sub(r'^(Narração|Narrador|Texto|Script|Voz|Roteiro)[:\s-]*', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # 5. Remover asteriscos de negrito/itálico que podem ser lidos estranho por alguns TTS
    text = text.replace("**", "").replace("__", "")
    
    # Limpeza de espaços extras
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def generate_audio(text: str, output_path: str, voice_id: str = None, sfx_path: str = None, emotion: str = "normal"):
    """
    Gera um arquivo de áudio narrando o texto usando o Typecast.ai (Vozes Profissionais).
    """
    api_key = os.getenv("TYPECAST_API_KEY")
    if not api_key:
        print("AVISO: TYPECAST_API_KEY não encontrada. Fallback para geração offline não disponível.")
        raise ValueError("API Key do Typecast.ai é obrigatória para esta versão.")

    selected_voice = voice_id if voice_id else DEFAULT_VOICE_ID
    print(f"Gerando áudio via Typecast.ai (Voz ID: {selected_voice}, Emoção: {emotion})...")
    client = Typecast(api_key=api_key)
    
    # Limpar texto de instruções indesejadas
    cleaned_text = _clean_narration_text(text)
    if not cleaned_text:
        print("AVISO: Texto vazio após limpeza. Usando texto original para evitar falha.")
        cleaned_text = text

    try:
        # Configuração do TTSRequest
        request = TTSRequest(
            text=cleaned_text,
            voice_id=selected_voice,
            model=TTSModel.SSFM_V21,
            prompt=Prompt(
                emotion_preset=emotion, # normal, happy, sad, angry
                emotion_intensity=1.2,
                tempo=1.25 # Aceleração para ritmo de Shorts (25% mais rápido)
            )
        )
        
        response = client.text_to_speech(request)
        
        # Salva o áudio binário temporariamente
        temp_tts = f"temp_typecast_{int(time.time())}.mp3"
        with open(temp_tts, "wb") as f:
            f.write(response.audio_data)

        # Processamento com Pydub (SFX e Normalização)
        narration = AudioSegment.from_file(temp_tts)
        
        if sfx_path and os.path.exists(sfx_path):
            print(f"Mixando efeito sonoro de {sfx_path}...")
            try:
                sfx = AudioSegment.from_file(sfx_path)
                sfx = sfx - 15  # Diminui volume do SFX
                narration = narration.overlay(sfx)
            except Exception as mix_e:
                print(f"Aviso na mixagem: {mix_e}")

        # Exporta o áudio final
        narration.export(output_path, format="mp3")
        
        # Limpeza
        if os.path.exists(temp_tts):
            os.remove(temp_tts)
            
        print(f"Áudio profissional salvo em {output_path}")
        return True

    except Exception as e:
        print(f"ERRO CRÍTICO no Typecast: {e}")
        raise e

if __name__ == "__main__":
    # Teste rápido
    os.makedirs("assets", exist_ok=True)
    generate_audio("A inteligência artificial transformou a maneira como criamos vídeos.", "assets/final_test_typecast.mp3", emotion="happy")
