from setuptools import setup

setup(
    name = "devpi-rss",
    version = "1.0.2",
    long_description=open("README.rst").read(),
    description="A plug-in for devpi-server which generates RSS feeds.",
    author='k-bu',
    url='https://github.com/k-bu/devpi-rss',
    install_requires = [
        "devpi-server>=2.2.2",
        "devpi-web>=2.4.0",
        "PyRSS2Gen",
        ],
    packages=['devpi_rss'],
    entry_points = {'devpi_server': ["devpi-rss=devpi_rss.main"]},
)
