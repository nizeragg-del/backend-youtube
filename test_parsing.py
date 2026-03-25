import re
import json

def mock_parse_logic(raw_text, topic="Original Topic"):
    # Extração do TÍTULO
    display_title = topic
    if "[TITLE]" in raw_text:
        try:
            # Pega o que está entre [TITLE] e [SCENE TEXT]
            title_part = raw_text.split("[TITLE]")[1].split("[SCENE TEXT]")[0].strip()
            if title_part:
                display_title = title_part
                print(f"DEBUG: Sub-tema extraído: {display_title}")
        except Exception as e:
            print(f"DEBUG: Erro ao extrair título: {e}")

    final_text = ""
    image_prompts = []
    scripts = []
    
    # Regex para extrair cenas
    blocks = re.findall(r'\[SCENE TEXT\](.*?)(?:\[SCENE IMAGE\])(.*?)(?=\[SCENE TEXT\]|\Z)', raw_text, re.DOTALL | re.IGNORECASE)
    
    if blocks:
        for t, p in blocks:
            t = t.replace('\\"', '"').replace("\\'", "'").strip()
            p = p.replace('\\"', '"').replace("\\'", "'").strip()
            if len(t) > 5 and len(p) > 5:
                scripts.append(t)
                image_prompts.append(p)
        final_text = " ".join(scripts).strip()
    
    return {
        "title": display_title,
        "text": final_text,
        "image_prompts": image_prompts
    }

# Simulação de resposta do Manus AI
mock_output = """
Aqui está o roteiro:
[TITLE] O Mistério das Pirâmides
[SCENE TEXT] Você sabia que as pirâmides do Egito foram construídas com precisão matemática?
[SCENE IMAGE] Cinematic wide shot of the Great Pyramid of Giza under a clear blue sky, highly detailed.
[SCENE TEXT] Milhares de trabalhadores dedicaram décadas para erguer essas maravilhas.
[SCENE IMAGE] Close up of ancient workers moving a massive stone block with ropes and wooden rollers.
"""

def test_parsing():
    print("Testando parsing com mockup...")
    result = mock_parse_logic(mock_output, "Egito Antigo")
    print(f"Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    assert result["title"] == "O Mistério das Pirâmides"
    assert "Você sabia" in result["text"]
    assert len(result["image_prompts"]) == 2
    print("PARED! Parsing funcionando perfeitamente.")

if __name__ == "__main__":
    test_parsing()
