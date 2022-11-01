import os
from setuptools import setup, find_packages

def find_version(*args):
    """ Find version string starting with __version__ in a file"""

    f_path = os.path.join(os.path.dirname(__file__), *args)
    with open(f_path) as f:
        for line in f:
            if line.startswith('__version__'):
                break
    version_strings = line.split('"')
    if len(version_strings) != 3:
        raise ValueError('Version string is not enclosed inside " ".')
    return version_strings[1]

def get_file_names(directory):
    paths=[]
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths
        
description = open('readme.md').read()
version_string = find_version('rgagui', '__init__.py')

files = get_file_names('rgagui/examples') + get_file_names('rgagui/ui/icons') \
        + get_file_names('rgagui/ui/images') + get_file_names('rgagui/ui/sounds')

setup(
    name='rgagui',
    version=version_string,
    description='GUI Interface for RGA Instruments and Tasks',
    packages=['rgagui', 'rgagui.ui', 'rgagui.base'],
    package_data={
        'rgagui': files,
        # get_file_names('rgagui/examples') ,
        # 'rgagui/ui': get_file_names('rgagui/ui/icons'),
    },

    long_description=description,
    long_description_content_type='text/markdown',    
    install_requires=[
        "PyQt5",
        "matplotlib",
        "playsound == 1.2.2",
        "rga >= 0.1.7"
    ],
    
    entry_points={
        'console_scripts': [
            'rgagui = rgagui.taskmain:main'
        ],
        
    },
)
