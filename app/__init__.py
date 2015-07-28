#!/usr/bin/env python
# coding: utf-8

from flask import Flask, render_template, request, _request_ctx_stack
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path= '/appinstall/static')
app.config.from_object('config')

db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

@app.template_filter('datetime_fmt')
def datetime_fmt_filter(dt):
    return dt.strftime('%Y/%m/%d %H:%M:%S')

from app.mod_app.controllers import mod_app as app_module
from app.mod_ipa.controllers import mod_ipa as ipa_module

app.register_blueprint(app_module)
app.register_blueprint(ipa_module)

db.create_all()

