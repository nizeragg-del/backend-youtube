import os
import subprocess
import json
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client # type: ignore
from dotenv import load_dotenv # type: ignore

# Carregar variáveis de ambiente
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_path, ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[Automation] Erro: SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não configurados.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Mapeamento de dias da semana (Sincronizado com o Frontend Scheduling.tsx)
DAYS_MAP = {
    0: 'Seg', 
    1: 'Ter', 
    2: 'Qua', 
    3: 'Qui', 
    4: 'Sex', 
    5: 'Sab', 
    6: 'Dom'
}

def run_automation():
    # 1. Definir o dia atual em Brasília (BRT -03:00)
    brt = timezone(timedelta(hours=-3))
    now_brt = datetime.now(brt)
    today_br_name = DAYS_MAP[now_brt.weekday()]
    
    print(f"[Automation] Data Atual (BRT): {now_brt.strftime('%Y-%m-%d %H:%M:%S')} ({today_br_name})")
    
    # 2. Buscar usuários com automação ativa
    try:
        response = supabase.table("user_configs").select("*").eq("automation_active", True).execute()
        active_configs = response.data
    except Exception as e:
        print(f"[Automation] Erro ao buscar configurações: {e}")
        return

    if not active_configs:
        print("[Automation] Nenhuma automação ativa encontrada.")
        return

    print(f"[Automation] Encontradas {len(active_configs)} configurações ativas. Filtrando por dia...")

    # 3. Filtrar pelo dia da semana
    for config in active_configs:
        user_id = config.get("user_id")
        schedule_days = config.get("schedule_days", [])
        
        # Se for uma string JSON, tenta converter (Supabase às vezes retorna como string ou lista dependendo da config)
        if isinstance(schedule_days, str):
            try:
                schedule_days = json.loads(schedule_days)
            except:
                schedule_days = []

        if today_br_name in schedule_days:
            print(f"[Automation] >>> PROCESSANDO: Usuário {user_id} para o tema: {config.get('script_theme')}")
            
            # 4. Executar o pipeline (main.py)
            params = [
                "python", "main.py",
                "--topic", config.get("script_theme", "Curiosidade sobre o espaço"),
                "--user_id", user_id,
                "--voice_id", config.get("voice_id", "tc_5f8d7b0de146f10007b8042f"),
                "--voice_language", config.get("voice_language", "Português"),
                "--speech_speed", str(config.get("speech_speed", 1.0))
            ]
            
            try:
                # Executa como subprocesso e aguarda
                result = subprocess.run(params, capture_output=True, text=True, check=True)
                print(f"[Automation] Sucesso para {user_id}:\n{result.stdout[-500:]}") # Mostra o fim do log
            except subprocess.CalledProcessError as e:
                print(f"[Automation] FALHA para {user_id}:\n{e.stderr}")
        else:
            print(f"[Automation] Ignorando {user_id}: Hoje ({today_br_name}) não está agendado em {schedule_days}")

if __name__ == "__main__":
    run_automation()
