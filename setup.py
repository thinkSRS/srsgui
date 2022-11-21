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
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


description = open('readme.md').read()
version_string = find_version('rgagui', '__init__.py')

files = get_file_names('rgagui/examples') + get_file_names('rgagui/ui/images')
setup(
    name='rgagui',
    version=version_string,
    description='GUI Interface for RGA Instruments and Tasks',
    packages=['rgagui', 'rgagui.ui', 'rgagui.base', 'rgagui.plots'],
    package_data={
        'rgagui': files,
        # get_file_names('rgagui/examples') ,
        # 'rgagui/ui': get_file_names('rgagui/ui/icons'),
    },

    long_description=description,
    long_description_content_type='text/markdown',    
    install_requires=[
        "pyqt5",
        "matplotlib",
        "rga >= 0.1.12"
    ],
    
    entry_points={
        'console_scripts': [
            'rgagui = rgagui.__main__:main'
        ],
        
    },

    license="GPL v3",
    keywords=["instrument control", "data acquisition", "data visualization"],
    author="Chulhoon Kim",
    author_email="chulhoonk@yahoo.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering"
    ]

)
