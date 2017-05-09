from os import listdir
from os.path import isfile, join
from json import dumps

sprites = [f for f in listdir('./sprites/') if isfile(join('./sprites/', f))]
sprites_out = []
for sp in sprites:
    sprites_out.append(dict(text=sp.split('.')[0].title(), value=sp, imageSrc='static/sprites/%s' % sp))

open('characters.js', 'w').write('var ddData = %s;' % dumps(sprites_out));
