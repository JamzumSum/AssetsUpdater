import pytest
from updater import github

up = None


def setup_module():
    # github.register_proxy({'https': 'http://127.0.0.1:7890'})
    global up
    up = github.GhUpdater(github.Repo('JamzumSum', 'QzEmoji'))


def test_latest():
    r = up.latest()
    assert r
    assert r.tag
    assert r.title


def test_asset():
    r = up.latest()
    a = r.assets()
    assert a
    f = list(filter(lambda i: i.name == 'emoji.db', a))
    assert len(f) == 1
    a = f[0]
    del f
    assert a.download_url


def test_all():
    r = up.all(None, True)
    assert r
