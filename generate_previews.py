import os
import sys

try:
    from tts_client import generate_audio
except Exception as e:
    print(f"ERRO ao importar tts_client: {e}")
    sys.exit(1)

VOICES = [
    {"name": "camila", "id": "tc_5f8d7b0de146f10007b8042f", "text": "Olá! Eu sou a Camila. Minha voz é perfeita para mensagens de fé e reflexão."},
    {"name": "carlos", "id": "tc_61b9a899a28a0b3f64b21d4f", "text": "Hola, soy Carlos. Puedo ayudarte con locuciones en español o portugués con um toque único."},
    {"name": "victoria", "id": "tc_6777669145604e14c7ff8f03", "text": "Hello, I am Victoria. I provide professional and clear narrations for your global projects."},
    {"name": "walter", "id": "tc_6837b58f80ceeb17115bb771", "text": "Greetings. I am Walter. My deep and mature voice is ideal for serious and impactful storytelling."},
    {"name": "nia", "id": "tc_684a5a7ba2ce934624b59c6e", "text": "Hi! I am Nia. Let's make something dynamic and energetic together!"},
    {"name": "elise", "id": "tc_686dc45bbd6351e06ee64daf", "text": "Hello there, I'm Elise. I'm here to provide a warm and inviting voice for your content."}
]

output_dir = r"c:\Users\ctb075\Desktop\pend\Nova pasta\project front\public\assets\previews"
os.makedirs(output_dir, exist_ok=True)

print(f"Iniciando geração de {len(VOICES)} prévias...")

for voice in VOICES:
    output_path = os.path.join(output_dir, f"{voice['name']}.mp3")
    print(f"Gerando áudio para {voice['name']}...")
    try:
        generate_audio(voice['text'], output_path, voice_id=voice['id'])
        print(f"✅ Sucesso: {output_path}")
    except Exception as e:
        print(f"❌ Erro em {voice['name']}: {e}")

print("\n--- Processo Finalizado ---")
