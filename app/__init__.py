#!/usr/bin/env python
# coding: utf-8

from flask import Flask, render_template, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='/appinstaller/static')
app.config.from_object('config')

db = SQLAlchemy(app)


@app.route('/', methods=['GET'])
@app.route('{0}'.format(app.config['URL_PREFIX']), methods=['GET'])
def index():
    return redirect(url_for('file.index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.template_filter('datetime_fmt')
def datetime_fmt_filter(dt):
    return dt.strftime('%Y/%m/%d %H:%M:%S')

from app.mod_app.controllers import mod_app as app_module
from app.mod_file.controllers import mod_file as file_module

app.register_blueprint(app_module)
app.register_blueprint(file_module)

db.create_all()
