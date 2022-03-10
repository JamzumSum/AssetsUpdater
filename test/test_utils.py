import pytest

from updater.github import GhUpdater
from updater.github import Repo
import updater.utils as updater


@pytest.fixture(scope="module")
def up():
    return GhUpdater(Repo("JamzumSum", "AssetsUpdater"))


def test_latest_asset(up):
    url = updater.get_latest_asset(up, "AssetsUpdater-0.1.tar.gz")
    assert url.download_url


def test_latest_asset_FN(up):
    pytest.raises(FileNotFoundError, updater.get_latest_asset, up, "QAQ")


def test_version_filter(up):
    rels = updater.version_filter(up, ">=0.0.1", num=3, pre=True)
    rels = list(rels)
    assert rels
