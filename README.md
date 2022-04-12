# AssetsUpdater

Update assets from network. This repo is a component of [QzEmoji][qzemoji].

[![python](https://img.shields.io/badge/python-%E2%89%A53.7%2C%3C4.0-blue)][homepage]
[![Test](https://github.com/JamzumSum/AssetsUpdater/actions/workflows/test.yml/badge.svg)](https://github.com/JamzumSum/AssetsUpdater/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/JamzumSum/AssetsUpdater?include_prereleases&logo=github)](https://github.com/JamzumSum/AssetsUpdater/releases)


## Install

~~~ shell
pip install AssetsUpdater@https://github.com/JamzumSum/AssetsUpdater.git
~~~

For supporting async-download:

~~~ shell
pip install AssetsUpdater[async]@https://github.com/JamzumSum/AssetsUpdater.git
~~~

## Example and Demo

Run `gh-assets` after installing this package.

``` shell
$ gh-assets JamzumSum QzEmoji
0. <0.3> 0.3
1. <0.2> 0.2
2. <0.1.2> 0.1.2
Choose a release [0]:
# 0.3
0. emoji.db
1. QzEmoji-0.3-py3-none-any.whl
2. QzEmoji-0.3.tar.gz
Choose an asset [0]:
32768
```

``` shell
$ gh-assets -h
usage: gh-assets [-h] [--proxy PROXY] [--spec SPEC] user repo

positional arguments:
  user                  GiHub user name
  repo                  GitHub repo name

optional arguments:
  -h, --help            show this help message and exit
  --proxy PROXY, -p PROXY
                        HTTPS_PROXY is read automatically, or you may override
                        it here.
  --spec SPEC, -s SPEC  such as '>=1.0' or '~=1.11'
```

You may find examples at `src/updater/github.py` or `test/test_*.py`.


## Licence

- [MIT](https://github.com/JamzumSum/AssetsUpdater/blob/master/LICENSE)


[qzemoji]: https://github.com/JamzumSum/QzEmoji "Transfer Qzone Emoji to text."
[homepage]: https://github.com/JamzumSum/AssetsUpdater "Update assets from network."
