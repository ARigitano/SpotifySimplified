[app]
title = SpotifySimplified
package.name = spotifysimplified
package.domain = org.spotifysimplified

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,env

version = 0.1
requirements = python3,kivy,spotipy,redis,certifi,urllib3,idna,charset-normalizer,requests,python-dotenv

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.accept_sdk_license = True

# Pinned: python-for-android's default release (2026.05.09) ships a Python 3.14.2
# host recipe whose bundled pip is broken (ImportError on BuildDependencyInstallError),
# breaking the pip-based install stage for pure-Python deps. 2024.01.21 uses the
# well-tested Python 3.11.5 and doesn't hit this.
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
