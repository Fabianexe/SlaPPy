from setuptools import setup, find_packages
from slappy import __version__

setup(
    name='SlaPPy',
    version=__version__,
    packages=find_packages(),
    url='',
    license=' GNU GPLv3',
    author='Fabian Gärtner',
    author_email='fabianexe@gmail.com',
    description='SlaPPy - Squiggle and Sequence Plotter in Python',
    install_requires=['dash', 'h5py', 'numpy', 'dash_daq', 'plotly', 'gunicorn'],
    entry_points={
        'console_scripts': [
            'slappy = slappy.__main__:main'
        ]
    },
)
