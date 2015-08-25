#!/usr/bin/env python
# coding: utf-8

import os, sys, shutil
import zipfile
import pytz

from flask import Blueprint, Flask, url_for, request, render_template, \
                  redirect, escape, Markup, make_response, send_file, \
                  Response, flash, g, jsonify
from werkzeug import secure_filename
from datetime import datetime, date, timedelta

from app import app, db
from app.mod_ipa.models import Ipa
from app.mod_app.models import App

mod_ipa = Blueprint('ipa', __name__, url_prefix = app.config['URL_PREFIX'] + '/ipa')

@mod_ipa.route('/', methods=['GET'])
@mod_ipa.route('/<int:app_id>', methods=['GET'])
def index(app_id=None):
    error = None
    applist = App.query.all()
    ipalist = []
    if app_id:
        ipalist = Ipa.query.filter_by(app_id=app_id).order_by(Ipa.created_at.desc()).all()

    return render_template('ipa/index.html', error=error, \
        app_list=applist, ipa_list=ipalist)

@mod_ipa.route('/<int:app_id>', methods=['POST'])
def create(app_id):
    error = None
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = app.config['UPLOADED_IPA_DIR']
            now = datetime.now(pytz.timezone('Asia/Tokyo'))
            date = '{0}-{1:0=2d}{2:0=2d}{3:0=2d}'.format(now.date().__str__(), now.hour, now.minute, now.second)
            path = os.path.join(path, date)
            if not os.path.exists(path):
                os.makedirs(path)
            filepath = os.path.join(path, filename)
            file.save(filepath)
            ipa = Ipa(app_id, filename, filepath, request.url_root)
            db.session.add(ipa)
            db.session.commit()

            # Remove old ipa, show latest 20
            old_ipalist = Ipa.query.filter_by(app_id=app_id).order_by(Ipa.created_at.desc()).limit(21).all()
            old_ipa = None
            if len(old_ipalist) > 20:
                old_ipa = old_ipalist[-1]
            if old_ipa:
                ipalist = Ipa.query.filter(Ipa.app_id == app_id, Ipa.created_at < old_ipa.created_at).all()
                for ipa in ipalist:
                    ipa.remove_ipa()
                    db.session.delete(ipa)
                db.session.commit()
            response = { 'status': 1 }
        else:
            response = { 'status': 2 }
    else:
        response = { 'status': 0 }
    return jsonify(response)


ALLOWED_EXTENSIONS = set(['ipa'])
def allowed_file(filename):
    '''
    Check the extension of the file to be uploaded
    '''
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
