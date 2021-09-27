import pytest
import updater
from updater.github import GhUpdater, Repo

up = None

def setup_module():
    global up
    up = GhUpdater(Repo('JamzumSum', 'QzEmoji'))

def test_latest_asset():
    url = updater.get_latest_asset(up, 'emoji.db')
    assert url.download_url

def test_latest_asset_FN():
    pytest.raises(FileNotFoundError, updater.get_latest_asset, up, 'QAQ')
