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


description = open('README.md').read()
version_string = find_version('srsgui', '__init__.py')

# files = get_file_names('srsgui/ui/images')
setup(
    name='srsgui',
    version=version_string,
    description='Framework to provide GUI to Python scripts controlling instruments using remote commands',
    packages=['srsgui', 'srsgui.ui', 'srsgui.ui.qt', 'srsgui.task',
              'srsgui.inst', 'srsgui.inst.communications'],
    package_data={
        'srsgui': ['../srsgui/ui/srslogo.jpg',
                   '../srsgui/examples/oscilloscope example/*.*',
                   '../srsgui/examples/oscilloscope example/instruments/*.*',
                   '../srsgui/examples/oscilloscope example/tasks/*.*',
                   ]
    },

    long_description=description,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    install_requires=[
        "pyserial>=3",
    ],
    extras_require={
        'gui': ['matplotlib', 'pyside2']
    },
    entry_points={
        'console_scripts': [
            'srsgui = srsgui.__main__:main'
        ],
    },

    license="MIT license",
    keywords=["instrument control", "data acquisition", "data visualization"],
    author="Chulhoon Kim",
    # author_email="chulhoonk@yahoo.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering"
    ]

)
