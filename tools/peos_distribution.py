"""Repository-only ZIP registry; the registry is never embedded in a ZIP."""
from io import BytesIO
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

REGISTRY = 'downloads/PUBLIC_PACKAGES.json'


def load_packages(root):
    path = Path(root) / REGISTRY
    if not path.is_file():
        return {}
    value = json.loads(path.read_text())
    entries = value['packages']
    result = {}
    for item in entries:
        name = item['path']
        if (not re.fullmatch(r'downloads/PEOS_GITHUB_PACKAGE_(?:rev[0-9]+\.[0-9]+|next_spec_[0-9]{8})\.zip', name)
                or not re.fullmatch('[0-9a-f]{64}', item['sha256'])
                or type(item['bytes']) is not int or not 0 < item['bytes'] < 20*1024*1024
                or item.get('class') != 'PUBLIC_SPECIFICATION_PACKAGE' or name in result):
            raise ValueError('invalid or duplicate public package entry')
        result[name] = item
    if not result or value['primary'] not in result:
        raise ValueError('a primary public package is required')
    return result


def archive_errors(data, excluded=()):
    from peos_public_release import forbidden_file
    issues = []
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            names = archive.namelist()
            if (len(names) != len(set(names)) or len(names) > 500
                    or sum(i.file_size for i in entries) > 64*1024*1024):
                return ['ARCHIVE_LIMIT_OR_DUPLICATE_MEMBER']
            for item in entries:
                p = PurePosixPath(item.filename)
                if (p.is_absolute() or '..' in p.parts or '\\' in item.filename
                        or 'downloads' in p.parts or item.is_dir()
                        or (item.external_attr >> 16) & 0o170000 == 0o120000
                        or item.flag_bits & 1):
                    issues.append('UNSAFE_OR_RECURSIVE_PACKAGE_MEMBER:' + item.filename)
                else:
                    issues.extend(item.filename + ':' + e for e in
                                  forbidden_file(item.filename, archive.read(item), excluded))
            if archive.testzip() is not None:
                issues.append('ARCHIVE_CRC')
            manifest = archive.read('PACKAGE_MANIFEST.txt').decode('utf-8')
            rows = {}
            for line in manifest.split('\nFILES:\n', 1)[1].splitlines():
                m = re.fullmatch(r'([0-9a-f]{64}) (\d+) (.+)', line)
                if not m or m[3] in rows:
                    issues.append('ARCHIVE_MANIFEST_ROW')
                    continue
                rows[m[3]] = (m[1], int(m[2]))
            actual = {n: (hashlib.sha256(archive.read(n)).hexdigest(), len(archive.read(n)))
                      for n in names if n != 'PACKAGE_MANIFEST.txt'}
            if rows != actual:
                issues.append('ARCHIVE_MANIFEST_BYTES_OR_PATHS_DIFFER')
    except (OSError, ValueError, KeyError, IndexError, UnicodeError, zipfile.BadZipFile):
        issues.append('INVALID_PUBLIC_PACKAGE_ARCHIVE')
    return issues


def registered_archive_errors(relative, data, item, excluded=()):
    if (len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']):
        return [relative + ':DISTRIBUTION_ARCHIVE_BYTES_DIFFER']
    return [relative + ':' + e for e in archive_errors(data, excluded)]


def distribution_errors(root):
    root = Path(root)
    if not (root / 'downloads').exists():
        return []
    try:
        packages = load_packages(root)
        if not packages:
            return ['DISTRIBUTION_REGISTRY_MISSING']
    except (ValueError, KeyError, TypeError):
        return ['DISTRIBUTION_REGISTRY_INVALID']
    errors = []
    for name, item in packages.items():
        path = root / name
        if not path.is_file() or path.is_symlink():
            errors.append('DISTRIBUTION_ARCHIVE_MISSING:' + name)
        elif len(path.read_bytes()) != item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            errors.append('DISTRIBUTION_ARCHIVE_BYTES_DIFFER:' + name)
    expected = ''.join(f"{item['sha256']}  {Path(name).name}\n" for name,item in sorted(packages.items()))
    sums = root / 'downloads/SHA256SUMS'
    if not sums.is_file() or sums.read_bytes() != expected.encode('ascii'):
        errors.append('DISTRIBUTION_CHECKSUMS_DIFFER')
    return errors
