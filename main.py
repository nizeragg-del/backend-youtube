import os
import subprocess
import shutil
import json
from dotenv import load_dotenv # type: ignore
from scripts.generate_script import generate_script # type: ignore
from scripts.generate_voice import generate_voice, get_audio_duration # type: ignore
from scripts.generate_images import generate_manus_image # type: ignore
from scripts.upload_youtube import upload_to_youtube # type: ignore
from supabase import create_client, Client # type: ignore

if not os.path.exists(".env") and os.path.exists(".env.example"):
    load_dotenv(".env.example")
else:
    load_dotenv()

def run_pipeline(topic: str, user_id: str = ""):
    print("=" * 40)
    print(f"🎬 Iniciando automação (V8 Manus AI) para: {topic}")
    
    # Configuração Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Chave secreta para bypass RLS no Actions
    
    # Chaves de API
    manus_key = os.getenv("MANUS_API_KEY", "")
    typecast_key = os.getenv("TYPECAST_API_KEY", "")
    yt_refresh = ""
    yt_client_id = ""
    yt_client_secret = ""

    if user_id and supabase_url and supabase_key:
        print(f"[Supabase] Buscando chaves para o usuário: {user_id}")
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
            response = supabase.table("user_configs").select("*").eq("user_id", user_id).execute()
            if response.data:
                config = response.data[0]
                manus_key = config.get("manus_api_key") or manus_key
                typecast_key = config.get("typecast_api_key") or typecast_key
                yt_refresh = config.get("youtube_refresh_token", "")
                yt_client_id = config.get("youtube_client_id", "")
                yt_client_secret = config.get("youtube_client_secret", "")
                print("[Supabase] Chaves do usuário carregadas com sucesso!")
            else:
                print("[Supabase] ⚠️ Nenhuma configuração encontrada para este usuário. Usando chaves padrão.")
        except Exception as e:
            print(f"[Supabase] 🔴 Erro ao buscar chaves: {e}")
    
    # Sobrescrever envs para os sub-scripts usarem as chaves corretas
    os.environ["MANUS_API_KEY"] = manus_key
    os.environ["TYPECAST_API_KEY"] = typecast_key
    
    print(f"[Config] Manus API Key: {'Configurada (Usuário)' if user_id and manus_key else ('Configurada' if manus_key else 'AUSENTE')}")
    print(f"[Config] Typecast API Key: {'Configurada (Usuário)' if user_id and typecast_key else ('Configurada' if typecast_key else 'AUSENTE')}")
    print("=" * 40)
    
    # Pastas de configuração
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    output_dir = os.path.join(base_dir, "output", "videos")
    
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # PASSO 1 - Manus AI: Roteiro
    print("\n[Passo 1] Solicitando novo roteiro e prompts ao Manus AI...")
    script_data = generate_script(topic)
    
    if not script_data or not isinstance(script_data, dict):
        print("🔴 ERRO: Não foi possível gerar o roteiro via Manus AI. Abortando.")
        return

    script_text = script_data.get("text", "")
    image_prompts = script_data.get("image_prompts", [])
    
    print(f"Roteiro final ({len(script_text)} caracteres):\n{script_text}\n")
    print(f"Encontrados {len(image_prompts)} prompts de imagem.\n")
    
    script_path = os.path.join(assets_dir, "script.txt")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(str(script_text))
        
    # PASSO 2 - Geração de Imagens via Manus AI
    print("[Passo 2] Gerando novas imagens da produção...")
    image_paths = []
    public_images_dir = os.path.join(base_dir, "remotion", "public", "assets", "images")
    
    # Limpa a pasta de imagens para garantir que não use lixo de produções anteriores
    if os.path.exists(public_images_dir):
        shutil.rmtree(public_images_dir)
    os.makedirs(public_images_dir, exist_ok=True)
    
    # Gera novas imagens obrigatoriamente
    for i in range(10):
        if image_prompts and i < len(image_prompts):
            print(f"  -> Gerando imagem {i+1}/{len(image_prompts)}...")
            prompt = str(image_prompts[i])
            path = generate_manus_image(prompt, i, public_images_dir)
            if path:
                image_paths.append(path)
        elif not image_prompts and not image_paths:
            # Fallback se não tiver nada
            print(f"  -> Sem prompt para cena {i}. Usando padrão.")
            path = generate_manus_image("Cinematic bible scene", i, public_images_dir)
            if path: image_paths.append(path)

    # PASSO 3 - Typecast AI: Narração e Sync
    print("[Passo 3] Gerando narração via Typecast AI...")
    audio_path_raw, sync_path_raw = generate_voice(str(script_text), assets_dir)
    
    if not audio_path_raw or not sync_path_raw:
        print("🔴 ERRO: Não foi possível gerar o áudio/sincronia via Typecast AI. Abortando.")
        return
    
    audio_path = str(audio_path_raw)
    sync_path = str(sync_path_raw)
    
    # Validação de duração para Shorts
    duration = get_audio_duration(audio_path)
    if duration and duration > 60:
        print(f"⚠️ AVISO: O vídeo final terá {duration:.2f}s, o que supera o limite de 60s dos Shorts!")
    
    # Copia os assets para a pasta public do remotion para o renderizador achar
    public_assets_dir = os.path.join(base_dir, "remotion", "public", "assets")
    os.makedirs(public_assets_dir, exist_ok=True)
    
    shutil.copy2(audio_path, os.path.join(public_assets_dir, "speech.mp3"))
    shutil.copy2(sync_path, os.path.join(public_assets_dir, "sync.json"))
    
    print("Arquivos de áudio e sincronização copiados para public/assets.")
    
    # PASSO 4 - Remotion: Renderização do Vídeo
    print("\n[Passo 4] Renderizando o vídeo no Remotion...")
    
    # Prepara um arquivo JSON de inputProps para o Remotion CLI
    input_props_path = os.path.join(assets_dir, "inputProps.json")
    
    # Lendo o sync.json
    try:
        with open(sync_path, "r", encoding="utf-8") as f:
            sync_data = json.load(f)
    except FileNotFoundError:
        sync_data = []
        
    props = {
        "title": topic,
        "scriptText": script_text,
        "imageUrls": image_paths,
        "syncData": sync_data,
        "audioUrl": "assets/speech.mp3" 
    }
    
    with open(input_props_path, "w", encoding="utf-8") as f:
        json.dump(props, f, indent=2, ensure_ascii=False)
        
    safe_topic = str(topic.replace(" ", "_").lower())
    short_name = safe_topic[0:15] if len(safe_topic) > 15 else safe_topic # type: ignore
    video_out_name = f"{short_name}.mp4"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    video_out_path = os.path.join(output_dir, video_out_name)
    
    # O comando do Remotion para renderizar a composição `MyComp` a partir dos props
    remotion_dir = os.path.join(base_dir, "remotion")
    props_arg = os.path.abspath(input_props_path).replace("\\", "/")
    out_arg = os.path.abspath(video_out_path).replace("\\", "/")
    
    cmd = [
        "npx", "remotion", "render",
        "src/index.ts", "ShortsComp", f'"{out_arg}"',
        "--props", f'"{props_arg}"'
    ]
    
    cmd_str = " ".join(cmd)
    print(f"Executando no Remotion: {cmd_str}")
    
    # subprocess call
    try:
        subprocess.run(cmd_str, cwd=remotion_dir, check=True, shell=True)
        print("\n" + "=" * 40)
        print(f"🟢 SUCESSO! Vídeo gerado em: {video_out_path}")
        print("=" * 40)
        
        # PASSO Final - YouTube Upload (Opcional)
        if yt_refresh and yt_client_id and yt_client_secret:
            try:
                upload_to_youtube(
                    video_path=video_out_path,
                    title=topic, # Usamos o tópico como título por enquanto
                    description=f"Vídeo gerado automaticamente sobre: {topic}\n\n#evangelico #fe #esperanca",
                    client_id=yt_client_id,
                    client_secret=yt_client_secret,
                    refresh_token=yt_refresh
                )
            except Exception as e:
                print(f"🔴 Erro no upload para o YouTube: {e}")
        else:
            print("[YouTube] Pulando upload automático (Chaves não configuradas).")
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 40)
        print(f"🔴 ERRO na renderização do vídeo: {e}")
        print("=" * 40)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, required=True)
    parser.add_argument("--user_id", type=str, default="")
    args = parser.parse_args()
    
    run_pipeline(args.topic, args.user_id)
