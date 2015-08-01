from setuptools import setup

setup(
    name = "devpi-rss",
    version = "1.0.3",
    long_description=open("README.rst").read(),
    description="A plug-in for devpi-server which generates an RSS feed for every index.",

    author="k-bu",
    url="https://github.com/k-bu/devpi-rss",
    license="MIT",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],

    install_requires = [
        "devpi-server>=2.2.2",
        "devpi-web>=2.4.0",
        "PyRSS2Gen",
        ],
    packages=["devpi_rss"],
    entry_points = {"devpi_server": ["devpi-rss=devpi_rss.main"]},
)
