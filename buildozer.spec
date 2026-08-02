[app]
title = SpotifySimplified
package.name = spotifysimplified
package.domain = org.spotifysimplified

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,env

version = 0.1
requirements = python3,kivy,spotipy,certifi,urllib3,idna,charset-normalizer,requests,python-dotenv

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
