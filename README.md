# SpotifySimplified

A minimal app that connects to one Spotify playlist and offers limited playback
controls (Play/Pause, Next, Previous) scoped to that playlist. Built with Kivy so
it can run on desktop for development and be packaged into an Android APK with
Buildozer.

## Status

The core app (`main.py`, `spotify_client.py`) is written and runnable on desktop
today. Android packaging config (`buildozer.spec`) is in place, but the OAuth
login flow currently relies on a local loopback redirect (`127.0.0.1`), which
works on desktop but **not** on a real Android device. Making login work on
Android requires capturing the redirect via a custom URL scheme and Android's
intent system — that's the next piece to build before this can run on a phone.

## Setup (desktop, for development)

1. Create a Spotify app at https://developer.spotify.com/dashboard.
   - Add `http://127.0.0.1:8888/callback` as a Redirect URI in the app settings.
2. Copy `.env.example` to `.env` and fill in:
   - `SPOTIFY_CLIENT_ID` from your Spotify app.
   - `SPOTIFY_PLAYLIST_ID` — the playlist URL, URI, or bare ID to control.
3. Create a virtual environment and install dependencies:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run it:
   ```
   python main.py
   ```
5. Click "Connect to Spotify", log in via the browser window that opens, and
   grant access. The app will start the configured playlist on your active
   Spotify device (desktop app, phone, or web player must already be open).

Note: playback control endpoints require a Spotify **Premium** account and at
least one active Spotify device.

## Android packaging (in progress)

`buildozer.spec` is configured to build an APK via:
```
buildozer android debug
```
This requires a Linux machine with the Android SDK/NDK (buildozer installs
most of this automatically on first run). The OAuth redirect handling still
needs Android-specific work before login will succeed on-device — see Status
above.
