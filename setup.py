from setuptools import setup

setup(
    name='eofetch',
    version='0.1',
    description='Earth Observation Data Retrieval library',
    author='S[&]T',
    license='BSD',
    packages=['eofetch'],
    entry_points={'console_scripts': ['eofetch = eofetch.main:main']},
    install_requires=['boto3', 'pystac-client', 'requests']
)
