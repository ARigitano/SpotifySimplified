import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.env"))

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
REDIRECT_URI = os.environ["SPOTIFY_REDIRECT_URI"]
PLAYLIST_ID = os.environ["SPOTIFY_PLAYLIST_ID"]

SCOPES = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
