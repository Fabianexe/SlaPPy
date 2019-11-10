from setuptools import setup, find_packages
from fipy import __version__

setup(
    name='FIPY',
    version=__version__,
    packages=find_packages(),
    url='',
    license=' GNU GPLv3',
    author='Fabian Gärtner',
    author_email='fabianexe@gmail.com',
    description='Fast5 In PrettY', install_requires=['dash', 'h5py', 'numpy', 'dash_daq', 'plotly'],
    entry_points={
        'console_scripts': [
            'fipy = fipy.__main__:main'
        ]
    },
)
