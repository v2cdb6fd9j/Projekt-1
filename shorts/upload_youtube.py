"""Upload to YouTube (Shorts = vertical video <= 60s) via the official Data API.

Setup: create an OAuth "Desktop app" client in Google Cloud Console, enable the
YouTube Data API v3, and save the JSON as credentials/client_secret.json.
First run opens a browser for consent; the token is cached per channel.
Note: videos uploaded by unverified API projects are locked private until the
project passes Google's audit.
"""
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _creds(channel_name: str) -> Credentials:
    token_path = f"credentials/token_{channel_name}.json"
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials/client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return creds


def upload(channel: dict, video_path: str, title: str, description: str, tags: list[str]) -> str:
    yt = build("youtube", "v3", credentials=_creds(channel["name"]))
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "27",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    req = yt.videos().insert(
        part="snippet,status", body=body, media_body=MediaFileUpload(video_path, resumable=True)
    )
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return f"https://youtube.com/shorts/{resp['id']}"
