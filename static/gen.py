from os import listdir
from os.path import isfile, join
from json import dumps

sprites = [f for f in listdir('./sprites/melee') if isfile(join('./sprites/melee', f))]
sprites_out = []
for sp in sprites:
    sprites_out.append(dict(text=sp.split('.')[0].title(), value=sp, imageSrc='static/sprites/melee/%s' % sp))

open('characters.txt', 'w').write(dumps(sprites_out));
