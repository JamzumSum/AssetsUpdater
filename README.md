# AssetsUpdater

Update assets from network. This repo is a component of [QzEmoji][qzemoji].

<div>

<img src="https://img.shields.io/badge/python-3.8%2F3.9-blue">

<a href="https://github.com/JamzumSum/AssetsUpdater/actions/workflows/test.yml">
<img src="https://github.com/JamzumSum/AssetsUpdater/actions/workflows/test.yml/badge.svg">
</a>

<a href="https://github.com/JamzumSum/AssetsUpdater/releases">
<img src="https://img.shields.io/github/v/release/JamzumSum/AssetsUpdater?include_prereleases&logo=github">
</a>

</div>

## Install

~~~ shell
pip install AssetsUpdater@https://github.com/JamzumSum/AssetsUpdater.git
~~~

For supporting async download: 

~~~ shell
pip install AssetsUpdater[async]@https://github.com/JamzumSum/AssetsUpdater.git
~~~

## Types

Python type annotation is fully supported.

**Updater**

> Only GitHub updater is implemented now.

`Updater` can:
- iterate all releases
- get latest release

**Release**

`Release` has:
- `tag`, `name`...

`Release` can:
- list all assets

**Assets**

`Asset` has:
- name
- download_url

## API and Examples

### Download Latest Assets

~~~ python
> from updater.github import GhUpdater, Repo
> up = GhUpdater(Repo(user, reponame))
> url = get_latest_asset(up, 'query.db', pre=False)   
> url 
'https://github.com/..../query.db'

> from updater.download import download
> progress = download(url, 'data/query.db') # progress is an iterator specifying download size
> list(progress)    # drop any result(download size)
~~~

*NOTE*: For async download, use `download.adownload`.

### Filter Tags using Regex

~~~ python
> from updater import tag_filter
> from updater.github import GhUpdater, Repo
> up = GhUpdater(Repo(user, reponame))
> beta = tag_filter(up, r"[\d\.]+b\d+.*", num=3, pre=True)   # include pre-release; limited to the first 3 results
> beta
['0.1.2b2.dev1', '0.1.2b1', '0.1.1b1']
~~~

> You can filter by release name as well. If regex is not enough, iterate on releases and filter by yourself is certainly supported.

## Licence

- [MIT](https://github.com/JamzumSum/AssetsUpdater/blob/master/LICENSE)

### Third Party

- aiohttp: [Apache-2.0](https://github.com/aio-libs/aiohttp/blob/master/LICENSE.txt)
- aiofiles: [Apache-2.0](https://github.com/Tinche/aiofiles/blob/master/LICENSE)


[qzemoji]: https://github.com/JamzumSum/QzEmoji "Transfer Qzone Emoji to text."
