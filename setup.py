from setuptools import setup

with open("README.md", 'r', encoding="utf-8") as f:
    long_description = f.read()

# with open("requirements.txt", 'r') as f:
#     install_requirements = list(f.read().splitlines())


setup(
    name='albedo-bot',
    version='1.0',
    description='A module for running a python Discord Bot for managing AFK '
    'arena rosters for players in AFK Arena',
    license="MIT",
    long_description=long_description,
    author='Nate Jensvold',
    author_email='jensvoldnate@gmail.com',
    # url="http://www.foopackage.com/",
    packages=['albedo_bot'],  # same as name
    # external packages as dependencies
    install_requires=["wheel", "bar"],
    scripts=[

    ]
)
