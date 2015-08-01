from setuptools import setup

readme = open("README.rst").read()

setup(
    name = "devpi-rss",
    version = "1.0.0",
    long_description=readme,
    description=readme[0:readme.find("\n")],
    install_requires = ["PyRSS2Gen"],
    entry_points = {'devpi_server': ["devpi-rss=devpi_rss.main"]},
)
