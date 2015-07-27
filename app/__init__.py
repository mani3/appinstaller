#!/usr/bin/env python
# coding: utf-8

from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

@app.before_request
def before_request():
    method = request.form.get('_method', '').upper()
    if method:
        request.environ['REQUEST_METHOD'] = method
        ctx = flask._request_ctx_stack.top
        ctx.url_adapter.default_method = method
        assert request.method == method

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

from app.mod_app.controllers import mod_app as app_module
from app.mod_ipa.controllers import mod_ipa as ipa_module

app.register_blueprint(app_module)
app.register_blueprint(ipa_module)

db.create_all()

