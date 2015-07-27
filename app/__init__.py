#!/usr/bin/env python
# coding: utf-8

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

from app.mod_ipa.controllers import mod_ipa as ipa_module

app.register_blueprint(ipa_module)

db.create_all()

