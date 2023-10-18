"""
Anomstack package setup.
"""

from setuptools import find_packages, setup

setup(
    name="anomstack",
    packages=find_packages(exclude=[]),
    install_requires=[
        "dagit",
        "dagster",
        "dagster-docker",
        "dagster-gcp",
        "dagster-gcp-pandas",
        "dagster-postgres",
        "dagster-webserver",
        "duckdb",
        "google-auth",
        "google-cloud-bigquery",
        "Jinja2",
        "matplotlib",
        "oscrypto",
        "pandas",
        "pandas-gbq",
        "pyod",
        "pyyaml",
        "snowflake-connector-python[pandas]",
        "boto3",
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
