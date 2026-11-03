"""Validate public download targets independently of Markdown page context."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

LANDING = 'https://github.com/fpb-e/PEOS/blob/main/downloads/README.md'


def pinned_download_url(commit, relative):
    if (not isinstance(commit, str) or not re.fullmatch('[0-9a-f]{40}', commit)
            or not re.fullmatch(r'downloads/PEOS_GITHUB_PACKAGE_(?:rev[0-9]+\.[0-9]+|next_spec_[0-9]{8})\.zip', relative)):
        raise ValueError('exact commit and public package path required')
    return 'https://raw.githubusercontent.com/fpb-e/PEOS/' + commit + '/' + relative


def download_link_errors(root):
    root = Path(root)
    readme = (root/'README.md').read_text()
    if not (root/'downloads').exists():
        return [] if '(' + LANDING + ')' in readme else ['PACKAGE_DISTRIBUTION_LANDING_MISSING']
    registry = json.loads((root/'downloads/PUBLIC_PACKAGES.json').read_text())
    primary = next((p for p in registry['packages'] if p['path'] == registry['primary']), None)
    if primary is None:
        return ['PRIMARY_DOWNLOAD_MISSING']
    try:
        url = pinned_download_url(primary.get('asset_commit'), primary['path'])
    except (TypeError, ValueError):
        return ['PRIMARY_DOWNLOAD_NOT_PINNED_TO_COMMIT']
    errors = []
    if primary.get('download_url') != url:
        errors.append('PRIMARY_DOWNLOAD_URL_DIFFERS')
    before, manual = readme.split('## インストールマニュアル\n', 1)
    for name, text in [('README_OVERVIEW', before), ('INSTALL_MANUAL', manual),
                       ('DOWNLOAD_PAGE', (root/'downloads/README.md').read_text())]:
        if '(' + url + ')' not in text:
            errors.append(name + '_PINNED_DOWNLOAD_MISSING')
    return errors
