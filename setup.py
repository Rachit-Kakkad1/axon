from setuptools import setup, find_packages

setup(
    name="agi_cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "rich",
        "google-generativeai",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "axon=agi_cli.main:main",
        ],
    },
)
