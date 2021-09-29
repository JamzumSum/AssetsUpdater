from setuptools import find_packages, setup

with open('src/updater/VERSION') as f:
    __version__ = f.read()

NAME = 'AssetsUpdater'
LOWER_NAME = NAME.lower()
PACKAGE = find_packages(where='src')

setup(
    name=NAME,
    version=__version__,
    description='Update assets from network.',
    author='JamzumSum',
    author_email='zzzzss990315@gmail.com',
    license="MIT",
    python_requires=">=3.8",                           # for f-string and := op
    install_requires=['requests', 'packaging'],
    extras_require={'async': ['aiohttp', 'aiofiles']},
    tests_require=['pytest'],
    packages=PACKAGE,
    package_dir={"": 'src'},
    include_package_data=True,
)
