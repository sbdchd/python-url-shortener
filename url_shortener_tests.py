#! /usr/bin/env python

import os
import unittest
import tempfile

import url_shortener

class UrlShortenerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, url_shortener.app.config['DATABASE'] = tempfile.mkstemp()
        url_shortener.app.config['TESTING'] = True
        self.app = url_shortener.app.test_client()
        url_shortener.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(url_shortener.app.config['DATABASE'])

    def test_index_page(self):
        rv = self.app.get('/')
        assert rv.status_code == 200

    def test_adding_url_db(self):
        rv = self.app.post('/', data=dict(
            shorten='http://github.com/'
            ), follow_redirects=True)
        assert 'URL:' in rv.data
        rv2 = self.app.get('/KDEsKQ')
        assert rv2.status_code == 302

    def test_404(self):
        rv = self.app.get('/random_url')
        assert rv.status_code == 404

if __name__ == '__main__':
    unittest.main()
