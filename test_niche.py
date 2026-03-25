import sys
import os

# Adiciona o diretório raiz ao path para importar os scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generate_script import generate_script

def test_v8_niche():
    niche = "Curiosidades sobre o Egito Antigo"
    print(f"Testando nicho: {niche}")
    result = generate_script(niche)
    
    if result:
        print("\n--- RESULTADO ---")
        print(f"Título Extraído: {result.get('title')}")
        print(f"Texto (primeiros 100 char): {result.get('text')[:100]}...")
        print(f"Prompts de Imagem: {len(result.get('image_prompts'))}")
    else:
        print("Erro ao gerar roteiro.")

if __name__ == "__main__":
    test_v8_niche()
