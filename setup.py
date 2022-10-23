from setuptools import setup, find_packages

setup(
    name='rgagui',
    version='0.1.0',
    
    packages= ['rgagui'],

    #include_package_data=True
    #long_description=open("README.txt").read(),
    install_requires=[
        "PyQt5",
        "matplotlib",
        "playsound"  
    ],
    
    entry_points={
        'console_scripts': [
            'rgagui = rgagui.calmain:main'
        ],
        
    },
)
