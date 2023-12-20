from setuptools import find_packages, setup


def read_requirements():
    with open('requirements.txt') as req:
        return req.read().splitlines()


setup(
    name='anomstack',
    version='0.0.9',
    packages=find_packages(),
    install_requires=read_requirements()
)
