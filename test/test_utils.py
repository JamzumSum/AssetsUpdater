import pytest
import updater.utils as updater
from updater.github import GhUpdater, Repo

up = None


def setup_module():
    global up
    up = GhUpdater(Repo('JamzumSum', 'AssetsUpdater'))


def test_latest_asset():
    url = updater.get_latest_asset(up, 'AssetsUpdater-0.1.tar.gz')
    assert url.download_url


def test_latest_asset_FN():
    pytest.raises(FileNotFoundError, updater.get_latest_asset, up, 'QAQ')


def test_version_filter():
    rels = updater.version_filter(up, '0.0.1', num=3, pre=True)
    rels = list(rels)
    assert rels
