import os

from setuptools import setup, find_packages
from slappy import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


name = 'SlaPPy'
setup(
    name=name,
    version=__version__,
    packages=find_packages(),
    url='https://github.com/Fabianexe/SlaPPy',
    license='GNU GPLv3',
    author='Fabian Gärtner',
    author_email='fabianexe@gmail.com',
    description='SlaPPy - Squiggle and Sequence Plotter in Python',
    install_requires=['dash', 'h5py', 'numpy', 'dash_daq', 'plotly', 'gunicorn', 'dash-bootstrap-components', 'visdcc'],
    entry_points={
        'console_scripts': [
            'slappy = slappy.__main__:main'
        ]
    },
    long_description=read('docs/README.md'),
    long_description_content_type='text/markdown',
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', __version__),
            'release': ('setup.py', __version__)
        }
    },
    keywords="nanopore, fast5, multi fast5, sequencing, plotting"

)
