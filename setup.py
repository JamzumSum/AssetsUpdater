from setuptools import find_packages, setup

NAME = 'AssetsUpdater'
LOWER_NAME = NAME.lower()
PACKAGE = find_packages(where='src')

setup(
    name=NAME,
    version='0.0.1',
    description='Update assets from network.',
    author='JamzumSum',
    author_email='zzzzss990315@gmail.com',
    license="MIT",
    python_requires=">=3.8",                          # for f-string and := op
                                                      # install_requires=[],
    install_requires=['requests'],
    extras_require={'async': ['aiohttp', 'aiofiles']},
    tests_require=['pytest'],
    packages=PACKAGE,
    package_dir={"": 'src'},
    include_package_data=True,
)
