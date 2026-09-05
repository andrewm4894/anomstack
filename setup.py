from pathlib import Path
import runpy

from setuptools import find_packages, setup

ROOT = Path(__file__).parent
VERSION = runpy.run_path(str(ROOT / "anomstack/__init__.py"))["__version__"]


def read_requirements():
    with open(ROOT / "requirements.txt") as req:
        return req.read().splitlines()


setup(
    name="anomstack",
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.12",
    install_requires=read_requirements(),
)
