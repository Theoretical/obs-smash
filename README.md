# obs-smash
OBS manager for Smash4 (or any other smash game) using Python 3.

* Pulls matches from challonge and auto updates stream matches based on winner.
* Speaks to OBS using obs-websocket.
* Auto-uploads VODs to youtube account provided.
* Easily manageable via tablet or phone.


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

# Dependencies
[Python 3.X](https://www.python.org/downloads/windows/) Tested with 3.6

[Flask](https://pypi.python.org/pypi/Flask) (pip install flask) Tested with 0.12

[Flask Cors](https://pypi.python.org/pypi/Flask-Cors) (pip install flask_cors) Tested with 3.0.2

[Google Api Python Client](https://pypi.python.org/pypi/google-api-python-client/) (pip install google-api-python-client) Tested with 1.6.2
