"""Regression coverage for numbered metadata and context-free URLs."""
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from peos_download_links import pinned_download_url, download_link_errors


class ReleaseDownloadTests(unittest.TestCase):
    def test_package_revision_and_all_current_document_headers_are_317(self):
        status=json.loads((ROOT/'admin/REV0.317_STATUS.json').read_text())
        restore=json.loads((ROOT/'runtime/PEOS_SESSION_RESTORE_rev0.317.json').read_text())
        self.assertEqual(status['target_revision'],'rev0.317')
        self.assertEqual(restore['candidate_revision'],'rev0.317')
        self.assertEqual(restore['authority']['current_canon'],'rev0.317')
        self.assertEqual(restore['authority']['accepted_baseline'],'PEOS_GITHUB_PACKAGE_rev0.316.zip')
        self.assertTrue(restore['candidate_accepted'])
        for p in (ROOT/'prompt').glob('*.md'):
            self.assertIn('- 文書revision: `rev0.317`',p.read_text())
            self.assertNotIn('次revisionは未採番',p.read_text().split('## 0. 文書の役割')[0])

    def test_download_does_not_depend_on_markdown_base_or_current_branch(self):
        url=pinned_download_url('a'*40,'downloads/PEOS_GITHUB_PACKAGE_rev0.317.zip')
        self.assertEqual(url,'https://raw.githubusercontent.com/fpb-e/PEOS/'+'a'*40+'/downloads/PEOS_GITHUB_PACKAGE_rev0.317.zip')
        self.assertNotIn('?raw=',url)

    def test_branch_names_and_unsafe_paths_cannot_be_download_pins(self):
        for commit,path in [('main','downloads/PEOS_GITHUB_PACKAGE_rev0.317.zip'),
                            ('a'*40,'../private.zip'),('a'*40,'downloads/PRIVATE_EVIDENCE.zip')]:
            with self.subTest(commit=commit,path=path),self.assertRaises(ValueError):
                pinned_download_url(commit,path)

    def test_current_distribution_links_match_the_exact_asset_commit(self):
        self.assertEqual(download_link_errors(ROOT),[])
