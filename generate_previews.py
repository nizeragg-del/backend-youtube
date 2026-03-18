import sys
import os

# Adicionar o diretório do vid ao path
vid_dir = r"c:\Users\ctb075\Desktop\pend\vid"
sys.path.append(vid_dir)

from tts_client import generate_audio

VOICES = [
    {"name": "Camila", "id": "tc_5f8d7b0de146f10007b8042f", "text": "Olá, eu sou a Camila. Minha voz é ideal para narrações inspiradoras e mensagens de fé."},
    {"name": "Ricardo", "id": "tc_5f2b8fdece0e550007ca5f55", "text": "E aí! Eu sou o Ricardo. Se você busca uma voz enérgica e impactante, eu sou a escolha certa."},
    {"name": "Fernanda", "id": "tc_63046f48a8044715bd5d214a", "text": "Olá, meu nome é Fernanda. Posso trazer um tom suave e acolhedor para as suas reflexões."},
    {"name": "Gabriel", "id": "tc_5f2b8fc5ce0e550007ca5f35", "text": "Fala pessoal! Aqui é o Gabriel. Minha voz é dinâmica e perfeita para conteúdos modernos."}
]

output_dir = r"c:\Users\ctb075\Desktop\pend\Nova pasta\project front\public\assets\previews"
os.makedirs(output_dir, exist_ok=True)

print(f"Gerando {len(VOICES)} prévias de voz...")

for voice in VOICES:
    output_path = os.path.join(output_dir, f"{voice['name'].lower()}.mp3")
    print(f"Gerando prévia para {voice['name']} (ID: {voice['id']})...")
    try:
        generate_audio(voice['text'], output_path, voice_id=voice['id'])
        print(f"✅ Salvo em: {output_path}")
    except Exception as e:
        print(f"❌ Erro ao gerar preview para {voice['name']}: {e}")

print("\nConcluído!")
