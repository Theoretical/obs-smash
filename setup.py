from glob import glob
from setuptools import setup, find_packages
import py2exe
import sys

NAME = "obs-smash"
VERSION = "0.5"

setup(
    name=NAME,
    version=VERSION,
    description="Manages OBS for streaming tournaments.",
    author="Everance",
    author_email='knidalee@gmail.com',
    url='',
    license='Free',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    options={
        'py2exe': {
            'packages':['jinja2'],
            'dist_dir': 'dist/test', # The output folder
            'compressed': True, # If you want the program to be compressed to be as small as possible
            'includes':['flask', 'flask_cors', 'json', 'requests', 'multiprocessing', 'socket', 'time', 'urlparse', 'os',
            'multiprocessing', 're', 'httplib', 'httplib2', 'os', 'random', 'sys', 'apiclient', 'oauth2client', 'yotube'], # All the modules you need to be included,  because py2exe guesses which modules are being used by the file we want to compile, but not the imports
        }
    },
    install_requires=[
        'Flask>=0.12.2',
        'Flask-Cors==3.0.2',
        'google-api-python-client>=1.6.2',
        'requests>=2.17.3',
    ],
    console=['obs-smash.py']
)
