# obs-smash
OBS manager for Smash4 (or any other smash game)
![Preview](http://puu.sh/uxTSZ/0f68f52a47.png)

# OBS
The OBS included is a manually compiled OBS with a custom obs-websocket.dll to add scene item management.

If you'd like to use your own just copy these files:
* data\obs-plugins\obs-websocket
* bin\Qt5Network.dll
* bin\Qt5WebSockets.dll
* obs-plugins\obs-websocket.dll

# Config
*config.json* contains all scene / html config.

*client_secrets.json* should contain your Youtube OAuth2 credentials.

# Sprites
I included the general Smash4 sprites we use for Terre Haute. You can copy these or use your own.

Note: changing sprites is a pain but check out ddData in templates/smash.html
