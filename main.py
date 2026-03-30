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

def run_pipeline(topic: str, user_id: str = "", voice_id: str = "", voice_language: str = "", 
                 speech_speed_arg: str = "1.0", video_type: str = "viral", 
                 image_references: str = "", phase: str = "all", generation_id: str = ""):
    print(f"[DEBUG] Executando run_pipeline | Phase: {phase} | Topic: {topic} | Type: {video_type}")
    speech_speed = float(speech_speed_arg) if speech_speed_arg.strip() else 1.0
    
    # Configuração Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
    
    # Busca configurações do usuário se necessário
    manus_key = os.getenv("MANUS_API_KEY", "")
    typecast_key = os.getenv("TYPECAST_API_KEY", "")
    yt_config = {"refresh": "", "id": "", "secret": ""}

    if user_id and supabase:
        try:
            response = supabase.rpc("get_user_secrets", {"p_user_id": user_id}).execute()
            if response.data:
                config = response.data[0] if isinstance(response.data, list) else response.data
                manus_key = config.get("manus_api_key") or manus_key
                typecast_key = config.get("typecast_api_key") or typecast_key
                yt_config["refresh"] = config.get("youtube_refresh_token") or ""
                yt_config["id"] = config.get("youtube_client_id") or os.getenv("YOUTUBE_CLIENT_ID", "")
                yt_config["secret"] = config.get("youtube_client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET", "")
        except Exception as e:
            print(f"[Supabase] Erro ao buscar chaves: {e}")

    os.environ["MANUS_API_KEY"] = manus_key
    os.environ["TYPECAST_API_KEY"] = typecast_key
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    output_dir = os.path.join(base_dir, "output", "videos")
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    script_data = None
    image_paths = []

    # --- PHASE 1: SCRIPTING ---
    if phase in ["all", "script"]:
        print("\n[Passo 1] Gerando roteiro e prompts...")
        img_refs = [url.strip() for url in image_references.split(",") if url.strip()]
        script_data = generate_script(topic, video_type=video_type, image_references=img_refs)
        
        if not script_data:
            print("🔴 ERRO: Script não gerado.")
            if generation_id and supabase:
                supabase.table("generations").update({"status": "failed"}).eq("id", generation_id).execute()
            return

        # Salva o resultado no Supabase se houver generation_id
        if generation_id and supabase:
            supabase.table("generations").update({
                "status": "awaiting_audio",
                "script_data": script_data
            }).eq("id", generation_id).execute()
            print(f"[Supabase] Geração {generation_id} atualizada: Aguardando escolha de áudio.")
            if phase == "script": return # Para aqui e aguarda o front

    # Se estivermos na Fase 2, precisamos recuperar o script_data do banco
    if phase == "render" and generation_id and supabase:
        print(f"[Passo 1.5] Recuperando dados da geração {generation_id}...")
        resp = supabase.table("generations").select("*").eq("id", generation_id).single().execute()
        if resp.data:
            script_data = resp.data.get("script_data")
            video_type = resp.data.get("video_type", video_type)

    if not script_data:
        print("🔴 ERRO: Dados do roteiro ausentes para renderização.")
        return

    script_text = script_data.get("text", "")
    image_prompts = script_data.get("image_prompts", [])
    actual_title = script_data.get("title", topic)
    actual_hashtags = script_data.get("hashtags", "#shorts #viral")

    # --- PASSO 2: IMAGENS ---
    print("[Passo 2] Gerando imagens...")
    public_images_dir = os.path.join(base_dir, "remotion", "public", "assets", "images")
    if os.path.exists(public_images_dir): shutil.rmtree(public_images_dir)
    os.makedirs(public_images_dir, exist_ok=True)

    for i in range(min(10, len(image_prompts) or 1)):
        prompt = image_prompts[i] if image_prompts and i < len(image_prompts) else f"Cinematic {actual_title}"
        path = generate_manus_image(str(prompt), i, public_images_dir)
        if path: image_paths.append(path)

    # --- PASSO 3: VOZ ---
    print(f"[Passo 3] Gerando narração ({voice_id})...")
    audio_path_raw, sync_path_raw = generate_voice(str(script_text), assets_dir, speech_speed=speech_speed)
    
    if not audio_path_raw or not sync_path_raw:
        print("🔴 ERRO: Áudio não gerado.")
        return
    
    audio_path, sync_path = str(audio_path_raw), str(sync_path_raw)
    public_assets_dir = os.path.join(base_dir, "remotion", "public", "assets")
    os.makedirs(public_assets_dir, exist_ok=True)
    shutil.copy2(audio_path, os.path.join(public_assets_dir, "speech.mp3"))
    shutil.copy2(sync_path, os.path.join(public_assets_dir, "sync.json"))

    # --- PASSO 4: RENDER ---
    print("\n[Passo 4] Renderizando no Remotion...")
    input_props_path = os.path.join(assets_dir, "inputProps.json")
    with open(sync_path, "r", encoding="utf-8") as f:
        sync_data = json.load(f)
        
    props = {
        "title": actual_title,
        "scriptText": script_text,
        "imageUrls": image_paths,
        "syncData": sync_data,
        "audioUrl": "assets/speech.mp3" 
    }
    
    with open(input_props_path, "w", encoding="utf-8") as f:
        json.dump(props, f, indent=2, ensure_ascii=False)
        
    import re
    safe_title = re.sub(r'[^a-zA-Z0-9]', '_', str(actual_title))[:25]
    video_out_path = os.path.join(output_dir, f"{safe_title}.mp4")
    
    remotion_dir = os.path.join(base_dir, "remotion")
    cmd = f'npx remotion render src/index.ts ShortsComp "{video_out_path.replace("\\", "/")}" --props "{os.path.abspath(input_props_path).replace("\\", "/")}"'
    
    try:
        subprocess.run(cmd, cwd=remotion_dir, check=True, shell=True)
        print(f"🟢 VÍDEO PRONTO: {video_out_path}")
        
        # Upload para Supabase Storage se for interativo
        if generation_id and supabase:
            print("[Supabase] Fazendo upload do vídeo...")
            with open(video_out_path, "rb") as f:
                storage_path = f"videos/{user_id}/{os.path.basename(video_out_path)}"
                supabase.storage.from_("generations").upload(storage_path, f.read(), {"content-type": "video/mp4", "x-upsert": "true"})
                video_url = supabase.storage.from_("generations").get_public_url(storage_path)
                supabase.table("generations").update({"status": "completed", "video_url": video_url}).eq("id", generation_id).execute()

        # YouTube Upload somente para automação (quando NÃO há generation_id vindo do chat interativo)
        is_automation = not generation_id
        if is_automation and yt_config["refresh"]:
            print("[YouTube] Iniciando upload automático (Automação)...")
            clean_title = re.sub(r'[\r\n\t]+', ' ', str(actual_title))
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()[:95]
            upload_to_youtube(
                video_path=video_out_path,
                title=clean_title,
                description=f"Automated video: {clean_title}\n\n{actual_hashtags}",
                client_id=yt_config["id"],
                client_secret=yt_config["secret"],
                refresh_token=yt_config["refresh"]
            )
    except Exception as e:
        print(f"🔴 ERRO: {e}")
        if generation_id and supabase:
            supabase.table("generations").update({"status": "failed"}).eq("id", generation_id).execute()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, required=True)
    parser.add_argument("--user_id", type=str, default="")
    parser.add_argument("--voice_id", type=str, default="")
    parser.add_argument("--voice_language", type=str, default="")
    parser.add_argument("--speech_speed", type=str, default="1.0")
    parser.add_argument("--video_type", type=str, default="viral")
    parser.add_argument("--image_references", type=str, default="")
    parser.add_argument("--phase", type=str, default="all")
    parser.add_argument("--generation_id", type=str, default="")
    args = parser.parse_args()
    
    run_pipeline(
        topic=args.topic, 
        user_id=args.user_id, 
        voice_id=args.voice_id, 
        voice_language=args.voice_language, 
        speech_speed_arg=args.speech_speed,
        video_type=args.video_type,
        image_references=args.image_references,
        phase=args.phase,
        generation_id=args.generation_id
    )
