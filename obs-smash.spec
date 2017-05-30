# -*- mode: python -*-

block_cipher = None


a = Analysis(['obs-smash.py', 'youtube.py'],
             pathex=['C:\\Users\\Everance\\Documents\\GitHub\\obs-smash'],
             binaries=[],
             datas=[
                ('config.json', '.'), ('client_secrets.json', '.'),
                ('templates/*', './templates/'), ('static/css/*', './static/css'),
                ('static/js/*', './static/js'),
                ('static/sprites/injustice2/*', './static/sprites/injustice2'),
                ('static/sprites/smash4/*', './static/sprites/smash4'),
                ('static/sprites/melee/*', './static/sprites/melee'),
                ('static/sprites/ggxrdrev2/*', './static/sprites/ggxrdrev2'),
             ],
             hiddenimports=['googleapiclient', 'apiclient', 'oauth2client'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='obs-smash',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='obs-smash')
