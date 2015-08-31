#! /usr/bin/env python

import sqlite3
from contextlib import closing
from datetime import datetime
import base64 as b

from flask import Flask, render_template, flash, request, redirect, \
                  url_for, g, abort

DATABASE = 'url_shortener.db'
DEBUG = False
SECRET_KEY = 'development key'
site_url = '127.0.0.1:5000/'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        base_url = request.form['shorten']
        check_url = g.db.execute('''SELECT shortened_url FROM url_shortener
                                    WHERE base_url = ?''',
                                    [base_url])
        shortened_url = check_url.fetchone()
        if shortened_url == None:
            date = str(datetime.utcnow())
            g.db.execute('''INSERT INTO url_shortener (base_url, date)
                            VALUES (?, ?);''',
                            [base_url, date])
            g.db.commit()
            primarykey = g.db.execute('''SELECT id FROM url_shortener
                                         WHERE base_url = ?''',
                                         [base_url])
            shortened_url = b.urlsafe_b64encode(str(primarykey.fetchone())
                                                    ).rstrip('=')
            g.db.execute('''UPDATE url_shortener set `shortened_url` = ?
                            WHERE base_url = ?;''',
                            [shortened_url, base_url])
            g.db.commit()
            link = shortened_url
        else:
            link = shortened_url[0]
        return render_template('index.html', link = site_url + link)
    return render_template('index.html')

@app.route('/<shortened_url>')
def shortened_url_redirects(shortened_url):
    convert_url = g.db.execute('''SELECT base_url FROM url_shortener
                                  WHERE shortened_url = ?''',
                                  [shortened_url])
    base_url = convert_url.fetchone()
    if base_url == None:
        abort(404)
    clean_url = base_url[0].encode('utf-8')
    return redirect(clean_url)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
