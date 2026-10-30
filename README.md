# SpotifySimplified

A minimal app that connects to one Spotify playlist and offers a single Next
button to skip tracks within that playlist. Built with Kivy so
it can run on desktop for development and be packaged into an Android APK with
Buildozer.

## Status

The app works on desktop and as an Android APK, including connecting to
Spotify on the phone. Once connected, it plays the configured playlist from its
first song and shows the current track's album cover above the Next button.

## Setup (desktop, for development)

1. Create a Spotify app at https://developer.spotify.com/dashboard.
   - Add `http://127.0.0.1:8888/callback` as a Redirect URI in the app settings.
2. Copy `settings.env.example` to `settings.env` (git-ignored; deliberately not a
   hidden file, because Buildozer skips dotfiles and it must be bundled into the
   APK) and fill in:
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
   grant access. The app will start the configured playlist from its first song
   on your active Spotify device (desktop app, phone, or web player must already
   be open) and show the song's cover.

Note: playback control endpoints require a Spotify **Premium** account and at
least one active Spotify device.

## Android packaging

`buildozer.spec` is configured to build an APK via:
```
pip install buildozer cython
buildozer android debug
```
The APK lands in `bin/`. Note that `settings.env` (including your Client ID and
playlist) gets bundled into the APK. `buildozer.spec` pins python-for-android to
`v2024.01.21` (Python 3.11) because the latest release's Python 3.14 toolchain
had a broken pip at the time of writing.
This requires a Linux machine with the Android SDK/NDK (buildozer installs
most of this automatically on first run).
