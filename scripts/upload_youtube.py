import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def upload_to_youtube(video_path, title, description, client_id, client_secret, refresh_token):
    """
    Faz o upload de um vídeo para o YouTube usando um refresh token.
    """
    print(f"[YouTube] Iniciando upload: {title}")
    
    # Configurar as credenciais a partir do refresh token
    credentials = google.oauth2.credentials.Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )

    # Renovar o access token se necessário
    if not credentials.valid:
        credentials.refresh(Request())

    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["ia", "automacao", "criatividade"],
            "categoryId": "22" # People & Blogs
        },
        "status": {
            "privacyStatus": "public", # Ou "unlisted" para testes
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[YouTube] Uploadando... {int(status.progress() * 100)}%")

    print(f"🟢 [YouTube] SUCESSO! Vídeo postado: https://www.youtube.com/watch?v={response['id']}")
    return response['id']
