import os

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
REDIRECT_URI = os.environ["SPOTIFY_REDIRECT_URI"]
PLAYLIST_ID = os.environ["SPOTIFY_PLAYLIST_ID"]

SCOPES = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
