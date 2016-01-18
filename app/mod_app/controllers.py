#!/usr/bin/env python
# coding: utf-8

from flask import Blueprint, url_for, render_template, request, redirect

from app import app, db
from app.mod_app.models import App

mod_app = Blueprint(
    'app', __name__, url_prefix=app.config['URL_PREFIX'] + '/app')


@mod_app.route('/', methods=['GET'])
def index():
    error = request.args.get('error', default=None)
    applist = App.query.all()
    return render_template('app/index.html', error=error, app_list=applist)


@mod_app.route('/', methods=['POST'])
def create():
    error = None
    app_name = request.form['app_name']
    platform = request.form['platform']
    app = App(app_name, platform)
    db.session.add(app)
    db.session.commit()
    return redirect(url_for('app.index', error=error))


@mod_app.route('/<int:id>', methods=['POST'])
def delete(id):
    error = None
    if request.form.get('_method') == 'DELETE':
        app = App.query.get(id)
        print app
        db.session.delete(app)
        db.session.commit()
    return redirect(url_for('app.index', error=error))
