from setuptools import setup

setup(
    name='eofetch',
    version='0.2',
    description='Earth Observation Data Retrieval library',
    url="https://github.com/stcorp/eofetch",
    author='S[&]T',
    license='BSD',
    packages=['eofetch'],
    entry_points={'console_scripts': ['eofetch = eofetch.__main__:main']},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=['boto3', 'pystac-client', 'requests']
)
