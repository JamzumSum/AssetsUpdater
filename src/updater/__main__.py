from .utils import version_filter
from .github import GhUpdater
import argparse


def main(url: str, spec: str = '', num: int = 5):
    up = GhUpdater(url)
    l = version_filter(up, spec, num)
    l = list(l)

    for i, r in enumerate(l):
        print(f'{i}.', repr(r))
    c = input('Choose a release: ')
    c = int(c)

    assert 0 <= c < len(l)
    print()
    for i in l[c].assets():
        print(f"{i.name}:", i.download_url)


if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument(
        'repo',
        help='GitHub repo url, such as https://github.com/JamzumSum/AssetsUpdater'
    )
    psr.add_argument('--spec', '-f', default='', help='such as >= 1.0, ~=1.11')

    arg = psr.parse_args()
    main(arg.repo, arg.spec)
