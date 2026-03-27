[app]

title = SpyGame
package.name = spygame
package.domain = org.yarik

source.dir = .
source.include_exts = py,png,jpg,gif,mp3,ttf
source.exclude_exts = pyc
source.exclude_dirs = tests, bin, lib, include

version = 0.1

requirements = python3==3.8.13,pygame-ce,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf

orientation = landscape
fullscreen = 1

android.permissions = INTERNET
android.api = 30
android.minapi = 21
android.ndk = 25b
android.sdk = 30

android.arch = arm64-v8a

android.add_assets = images, music

android.enable_androidx = True

android.allow_backup = True

android.manifest.orientation = landscape

android.presplash = images/menufon.png
android.icon = images/menufon.png

[buildozer]

log_level = 2

warn_on_root = 1

android.accept_sdk_license = True
