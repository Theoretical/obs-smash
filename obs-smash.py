from flask import Flask, jsonify, render_template, request, Response
from flask_cors import CORS, cross_origin
from json import dumps, loads
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

class Tournament(object):
    def __init__(self):
        self.config = loads(open('config.json', 'r').read())
        self.key = self.config['CHALLONGE_API_KEY']
        self.name = None
        self.slug = None
        self.history = dict(player1=set(), player2=set())
        self.event = None
        self.phases = []
        self.is_smash_gg = False
        self.app = Flask(__name__)

        self.build_routes()
        CORS(self.app)

    def build_routes(self):
        self.app.add_url_rule('/', 'index', self.on_index)
        self.app.add_url_rule('/settings', 'settings', self.on_settings, methods=['GET', 'POST'])
        self.app.add_url_rule('/settings/config', 'config', self.on_config)
        self.app.add_url_rule('/tournament/events', 'events', self.on_events, methods=['POST'])
        self.app.add_url_rule('/tournament/players', 'players', self.on_players, methods=['POST'])
        self.app.add_url_rule('/tournament/brackets', 'brackets', self.on_brackets, methods=['POST'])
        self.app.add_url_rule('/tournament/name', 'name', self.on_name, methods=['POST'])
        self.app.add_url_rule('/challonge/update', 'challonge_update', self.on_challonge_update, methods=['POST'])
        self.app.add_url_rule('/match/end', 'match_end', self.on_match_end, methods=['POST'])

    def on_index(self):
        hostname = gethostname()
        lan_ip = gethostbyname(hostname)
        return render_template('smash.html', ip=lan_ip, config=self.config)

    def on_settings(self):
        if request.method != 'POST':
            self.config = loads(request.form['settings'])
            open('config.json', 'w').write(dumps(config, indent=4))

            print('Reloaded settings file!')
            return jsonify({})

        hostname = gethostname()
        lan_ip = gethostbyname(hostname)
        return render_template('settings.html', ip=lan_ip)

    def on_config(self):
        return jsonify(self.config)

    def on_events(self):
        self.is_smash_gg = True
        url = request.form['url']

        if url[-1] == '/': url = url[:-1]
        slug = url.split('/')[-1]

        self.slug = slug
        res = get('https://api.smash.gg/tournament/{slug}?expand[]=event&expand[]=phase'.format(slug=slug))
        return jsonify(res.json())

    def on_players(self):
        url = request.form['url']

        if 'smash.gg' not in url:
            parsed = urlparse(url)

            team = parsed.netloc.strip('www.').split('.')[0]
            team = team + '-' if team != 'challonge' else ''

            challonge_id = team + parsed.path[1:]
            self.slug = challonge_id

            res = get('https://api.challonge.com/v1/tournaments/{id}.json?api_key={key}'.format(id=challonge_id, key=self.key))

            self.name = res.json()['tournament']['name']
            print ('%s | %s' % (challonge_id, team))
            return jsonify(get('https://api.challonge.com/v1/tournaments/{id}/participants.json?api_key={key}'.format(id=challonge_id, key=self.key)).json())

        # smash.gg logic.
        self.phases = []
        self.is_smash_gg = True

        event_slug = url.split('smash.gg/')[1].split('/overview')[0].replace('/events/', '/event/')
        res = get('https://api.smash.gg/tournament/{slug}?expand[]=event&expand[]=entrants&expand[]=phase&expand[]=groups'.format(slug=self.slug))
        self.name = res.json()['entities']['tournament']['name']

        return jsonify(res.json())

    def on_brackets(self):
        if not self.is_smash_gg:
            data = get('https://api.challonge.com/v1/tournaments/{id}/matches.json?api_key={key}'.format(id=self.slug, key=self.key)).json()
            return jsonify(data)

        groups = []
        res = get('https://api.smash.gg/tournament/{slug}?expand[]=groups'.format(slug=self.slug))
        for group in res.json()['entities']['groups']:
            if group['phaseId'] == int(request.form['phase']):
                groups.append(group['id'])

        data = get('https://api.smash.gg/phase_group/{phase}?expand[]=sets'.format(phase=request.form['phase'])).json()
        sets = []
        for phase in groups:
            data = get('https://api.smash.gg/phase_group/{phase}?expand[]=sets'.format(phase=phase)).json()
            sets.extend(data['entities']['sets'])

        return jsonify(sets)

    def on_challonge_update(self):
        url = 'https://api.challonge.com/v1/tournaments/{id}/matches/{match}.json?api_key={key}&match[scores_csv]={score}&match[winner_id]={winner}'.format(id=self.slug, match=request.form['match'],
            key=self.key, score=request.form['score'], winner=request.form['winner'])
        return jsonify(put(url).json())

    def on_name(self):
        self.name = request.form['name']
        return jsonify({})

    def on_match_end(self):
        global YOUTUBE_QUEUE # global upload process.
        sleep(4) # Sleep for 4s to make sure our recording is saved.

        RECORDING_DIRECTORY = self.config['RECORDING_DIRECTORY']
        file_list = [join(RECORDING_DIRECTORY, f) for f in listdir(RECORDING_DIRECTORY) if isfile(join(RECORDING_DIRECTORY, f))]
        latest_recording = max(file_list, key=getmtime)

        # rename recording.
        player1 = request.form['player1']
        player2 = request.form['player2']
        matchType = request.form['matchType']

        # recording name. (max 100 char.)
        recording_name = sub(r'[<>:"/\|?*]', '', '{matchType}-{player1} vs. {player2} - {tournament}'.format(matchType=matchType, player1=player1, player2=player2, tournament=self.name))[:100]

        n = 1
        while join(RECORDING_DIRECTORY, recording_name + '.mp4') in file_list:
            recording_name = sub(r'[<>:"/\|?*]', '', '{matchType}-{player1} vs. {player2} - {tournament} ({n})'.format(matchType=matchType, player1=player1, player2=player2, tournament=self.name, n=n))[:100]
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

    tournament = Tournament()
    tournament.app.run('0.0.0.0')
    YOUTUBE_PROCESS = Process(target=youtube_process, args=([YOUTUBE_QUEUE])).start()
