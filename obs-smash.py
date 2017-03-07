from flask import Flask, jsonify, render_template, request, Response
from flask_cors import CORS, cross_origin
from json import loads
from multiprocessing import Process, Queue
from oauth2client.tools import argparser
from os import listdir, rename
from os.path import getmtime, isfile, join
from re import sub
from requests import get, put
from socket import gethostname, gethostbyname
from time import sleep
from urllib.parse import urlparse
from youtube import get_authenticated_service, initialize_upload

app = Flask(__name__)
CORS(app)

config = loads(open('config.json', 'r').read())
CHALLONGE_API_KEY = config['CHALLONGE_API_KEY'] # Sam
CHALLONGE_TOURNAMENT_ID = ''
CHALLONGE_TOURNAMENT_NAME = ''
RECORDING_DIRECTORY = config['RECORDING_DIRECTORY']
argparser.add_argument("--file", required=True)
argparser.add_argument("--title")
argparser.add_argument("--description")
argparser.add_argument("--category")
argparser.add_argument("--keywords")
argparser.add_argument("--privacyStatus", default="PUBLIC")
YOUTUBE_QUEUE = Queue()


def youtube_process(queue):
    while True:
        args = queue.get(block=True)
        youtube = get_authenticated_service(args)
        initialize_upload(youtube, args)

@app.route('/')
def main_page():
    hostname = gethostname()
    lan_ip = gethostbyname(hostname)
    return render_template('smash.html', ip=lan_ip, config=config)


@app.route('/challonge/find', methods=['POST'])
def challonge_find():
    global CHALLONGE_TOURNAMENT_ID, CHALLONGE_TOURNAMENT_NAME
    url = request.form['url']
    parsed = urlparse(url)

    team = parsed.netloc.strip('www.').split('.')[0]
    team = team + '-' if team != 'challonge' else ''

    challonge_id = team + parsed.path[1:]
    CHALLONGE_TOURNAMENT_ID = challonge_id

    res = get('https://api.challonge.com/v1/tournaments/{id}.json?api_key={key}'.format(id=challonge_id, key=CHALLONGE_API_KEY))

    CHALLONGE_TOURNAMENT_NAME = res.json()['tournament']['name']
    print ('%s | %s' % (challonge_id, team))
    return jsonify(get('https://api.challonge.com/v1/tournaments/{id}/participants.json?api_key={key}'.format(id=challonge_id, key=CHALLONGE_API_KEY)).json())

@app.route('/challonge/matches', methods=['POST'])
def challonge_matches():
    global CHALLONGE_TOURNAMENT_ID
    data = get('https://api.challonge.com/v1/tournaments/{id}/matches.json?api_key={key}'.format(id=CHALLONGE_TOURNAMENT_ID, key=CHALLONGE_API_KEY)).json()
    return jsonify(data)

@app.route('/challonge/update', methods=['POST'])
def challonge_update():
    global CHALLONGE_TOURNAMENT_ID
    url = 'https://api.challonge.com/v1/tournaments/{id}/matches/{match}.json?api_key={key}&match[scores_csv]={score}&match[winner_id]={winner}'.format(id=CHALLONGE_TOURNAMENT_ID, match=request.form['match'],
        key=CHALLONGE_API_KEY, score=request.form['score'], winner=request.form['winner'])
    return jsonify(put(url).json())

@app.route('/name', methods=['POST'])
def name():
    global CHALLONGE_TOURNAMENT_NAME
    CHALLONGE_TOURNAMENT_NAME = request.form['name']
    return jsonify({})

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    #if request.method == 'POST':
        #stuff
    return render_template('settings.html')

@app.route('/recording/stop', methods=['POST'])
def recording_stop():
    global CHALLONGE_TOURNAMENT_NAME, YOUTUBE_QUEUE
    sleep(4) # Sleep for 4s to make sure our recording is saved.

    file_list = [join(RECORDING_DIRECTORY, f) for f in listdir(RECORDING_DIRECTORY) if isfile(join(RECORDING_DIRECTORY, f))]
    latest_recording = max(file_list, key=getmtime)

    # rename recording.
    player1 = request.form['player1']
    player2 = request.form['player2']
    matchType = request.form['matchType']

    # recording name. (max 100 char.)
    recording_name = sub(r'[<>:"/\|?*]', '', '{matchType}-{player1} vs. {player2} - {tournament}'.format(matchType=matchType, player1=player1, player2=player2, tournament=CHALLONGE_TOURNAMENT_NAME))[:100]

    n = 1
    while join(RECORDING_DIRECTORY, recording_name + '.mp4') in file_list:
        recording_name = sub(r'[<>:"/\|?*]', '', '{matchType}-{player1} vs. {player2} - {tournament} ({n})'.format(matchType=matchType, player1=player1, player2=player2, tournament=CHALLONGE_TOURNAMENT_NAME, n=n))[:100]
        n += 1

    file_name = join(RECORDING_DIRECTORY, recording_name + '.mp4')
    rename(latest_recording, file_name)

    # upload the video.
    youtube_args = argparser.parse_args([
        '--file', file_name,
        '--title', recording_name,
        '--description', config['YOUTUBE_DESCRIPTION'],
        '--keywords', config['YOUTUBE_KEYWORDS']
    ])

    YOUTUBE_QUEUE.put(youtube_args)
    return jsonify({})

if __name__ == '__main__':
    hostname = gethostname()
    lan_ip = gethostbyname(hostname)
    print ('Smash4 Stream Manager: http://{ip}:5000'.format(ip=lan_ip))
    app.run('0.0.0.0')
    YOUTUBE_PROCESS = Process(target=youtube_process, args=([YOUTUBE_QUEUE])).start()
