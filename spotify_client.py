import spotipy
from spotipy.oauth2 import SpotifyPKCE

import config


class NoActiveDeviceError(Exception):
    """Raised when there's no Spotify device open to play music on."""


class SpotifyController:
    """Thin wrapper around spotipy, scoped to controlling a single playlist."""

    # Sets up the PKCE auth manager (no client secret needed) and the spotipy client.
    def __init__(self, cache_path=".cache"):
        auth_manager = SpotifyPKCE(
            client_id=config.CLIENT_ID,
            redirect_uri=config.REDIRECT_URI,
            scope=config.SCOPES,
            cache_path=cache_path,
            open_browser=True,
        )
        self._sp = spotipy.Spotify(auth_manager=auth_manager)

    # Finds the currently active device, falling back to the first available one.
    def _active_device_id(self):
        devices = self._sp.devices().get("devices", [])
        for device in devices:
            if device.get("is_active"):
                return device["id"]
        return devices[0]["id"] if devices else None

    # Starts playback of the configured playlist from the beginning on an active device.
    def start_playlist(self):
        device_id = self._active_device_id()
        if device_id is None:
            raise NoActiveDeviceError("Open Spotify on a device first, then try again.")
        self._sp.start_playback(device_id=device_id, context_uri=self._playlist_uri())

    # Normalizes the configured playlist URL/URI/ID into a canonical spotify:playlist: URI.
    def _playlist_uri(self):
        playlist_id = config.PLAYLIST_ID
        if playlist_id.startswith("spotify:playlist:"):
            return playlist_id
        if "playlist/" in playlist_id:
            playlist_id = playlist_id.split("playlist/")[1].split("?")[0]
        return f"spotify:playlist:{playlist_id}"

    # Resumes playback on whatever device/context is currently paused.
    def play(self):
        self._sp.start_playback()

    # Pauses playback on the active device.
    def pause(self):
        self._sp.pause_playback()

    # Skips to the next track within the current context.
    def next_track(self):
        self._sp.next_track()

    # Goes back to the previous track within the current context.
    def previous_track(self):
        self._sp.previous_track()

    # Returns a dict describing what's playing, or None if nothing is.
    def get_current_playback(self):
        playback = self._sp.current_playback()
        if not playback or not playback.get("item"):
            return None
        item = playback["item"]
        return {
            "track_name": item["name"],
            "artist_name": ", ".join(a["name"] for a in item["artists"]),
            "is_playing": playback["is_playing"],
            "in_target_playlist": self._is_target_playlist(playback.get("context")),
        }

    # Checks whether the given playback context is the configured target playlist.
    def _is_target_playlist(self, context):
        if not context or context.get("type") != "playlist":
            return False
        return context.get("uri") == self._playlist_uri()
