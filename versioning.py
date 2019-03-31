import sys
from subprocess import check_output, STDOUT, CalledProcessError


def _get_git_version():
    try:
        tag_describe = check_output(
            'git describe --tags', shell=True, stderr=STDOUT
        ).strip().decode('utf-8')
    except CalledProcessError as e:
        print('[!] Can not detect version in git repo: ', e, file=sys.stderr)
        return 0, 0, 0, None, None
    else:
        if '-' in tag_describe:
            tag, describe = tag_describe.split('-', 1)
        else:
            tag, describe = tag_describe, None

    segs = tag.split('.')
    assert 1 < len(segs) <= 3

    major = int(segs[0])
    if len(segs) == 2:
        minor = int(segs[1])
        patch = None
    elif len(segs) == 3:
        minor = int(segs[1])
        patch = int(segs[2])

    if describe:
        dev, localversion = describe.split('-', 1)
        dev = int(dev)
    else:
        dev = localversion = None

    return major, minor, patch, dev, localversion


# pylama:ignore=C901
def version(major=0, minor=None, patch=None, localversion='auto'):
    repo_version = _get_git_version()
    is_dev = False

    if major == repo_version[0]:
        v = str(major)
    elif major > repo_version[0]:
        is_dev = True
        v = str(major)
    else:
        assert False

    if minor:
        if minor == repo_version[1]:
            v = '{}.{}'.format(v, minor)
        elif minor > repo_version[1]:
            is_dev = True
            v = '{}.{}'.format(v, minor)
        else:
            assert False

    if patch:
        if patch == repo_version[2]:
            v = '{}.{}'.format(v, patch)
        elif patch > repo_version[2]:
            is_dev = True
            v = '{}.{}'.format(v, patch)
        else:
            assert False

    if is_dev:
        v = '{}.dev{}'.format(v, repo_version[3] or 0)
    elif repo_version[3]:
        is_dev = True
        v = '{}.post1.dev{}'.format(v, repo_version[3])

    if localversion != 'auto' and localversion:
        v = '{}+{}'.format(v, localversion)

    if is_dev and repo_version[3] and localversion == 'auto':
        v = '{}+{}'.format(v, repo_version[4])

    return v
