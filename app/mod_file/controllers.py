#!/usr/bin/env python
# coding: utf-8

import os
import pytz

from flask import Blueprint, request, render_template, jsonify
from werkzeug import secure_filename
from datetime import datetime

from app import app, db
from app.mod_file.models import Ipa, Apk
from app.mod_app.models import App

mod_file = Blueprint(
    'file', __name__, url_prefix=app.config['URL_PREFIX'] + '/file')


@mod_file.route('/', methods=['GET'])
@mod_file.route('/<int:app_id>', methods=['GET'])
def index(app_id=None):
    error = None
    ua = request.headers.get('User-Agent')
    host = request.headers.get('Host')
    applist = App.query.all()
    ipalist = []
    apklist = []
    if app_id:
        ipalist = Ipa.query.filter_by(app_id=app_id).order_by(
            Ipa.created_at.desc()).all()
        apklist = Apk.query.filter_by(app_id=app_id).order_by(
            Apk.created_at.desc()).all()

    return render_template(
        'file/index.html', error=error, app_list=applist, ipa_list=ipalist,
        apk_list=apklist, is_mobile=is_mobile(ua), hostname=host)


@mod_file.route('/<int:app_id>', methods=['POST'])
def create(app_id):
    if request.method == 'POST':
        app = App.query.filter_by(id=app_id).first()
        if not app:
            return jsonify({'status': 0, 'error': 'Not found application'})

        file = request.files['file']
        if app.platform == 'ios':
            if file and allowed_ipa_file(file.filename):
                filename = secure_filename(file.filename)
                path = create_app_directory()
                filepath = os.path.join(path, filename)
                file.save(filepath)

                ipa = Ipa(app_id, filename, filepath, request.url_root)
                db.session.add(ipa)
                db.session.commit()
                remove_old_ipa(app_id)
                response = {'status': 1}
            else:
                return jsonify(
                    {
                        'status': 0,
                        'error': 'This file is not allowed(Not found ipa file)'
                    }
                )
        elif app.platform == 'android':
            if file and allowed_apk_file(file.filename):
                filename = secure_filename(file.filename)
                path = create_app_directory()
                filepath = os.path.join(path, filename)
                file.save(filepath)

                apk = Apk(app_id, filename, filepath, request.url_root)
                db.session.add(apk)
                db.session.commit()
                remove_old_apk(app_id)
                response = {'status': 1}
            else:
                return jsonify(
                    {
                        'status': 0,
                        'error': 'This file is not allowed(Not found apk file)'
                    }
                )
        else:
            return jsonify({'status': 0, 'error': 'Not found application'})
    else:
        response = {'status': 0, 'error': 'This URI is GET method only.'}
    return jsonify(response)


ALLOWED_IPA_EXTENSIONS = set(['ipa'])


def allowed_ipa_file(filename):
    '''
    Check the extension of the file to be uploaded
    '''
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_IPA_EXTENSIONS


ALLOWED_APK_EXTENSIONS = set(['apk'])


def allowed_apk_file(filename):
    '''
    Check the extension of the file to be uploaded
    '''
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_APK_EXTENSIONS


def is_mobile(useragent):
    '''
    Check mobile device from user agent
    '''
    if 'iPhone' in useragent or 'Android' in useragent:
        return True
    return False


def create_app_directory():
    path = app.config['UPLOADED_IPA_DIR']
    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    dirname = '{0}-{1:0=2d}{2:0=2d}{3:0=2d}{4:0=6d}'.format(
        now.date().__str__(), now.hour, now.minute,
        now.second, now.microsecond)
    path = os.path.join(path, dirname)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def remove_old_ipa(app_id):
    # Remove old ipa, show latest 20
    old_ipalist = Ipa.query.filter_by(app_id=app_id).order_by(
        Ipa.created_at.desc()).limit(21).all()
    old_ipa = None
    if len(old_ipalist) > 20:
        old_ipa = old_ipalist[-1]
    if old_ipa:
        ipalist = Ipa.query.filter(
            Ipa.app_id == app_id, Ipa.created_at < old_ipa.created_at).all()
        for ipa in ipalist:
            ipa.remove_ipa()
            db.session.delete(ipa)
        db.session.commit()


def remove_old_apk(app_id):
    # Remove old apk, show latest 20
    old_apklist = Apk.query.filter_by(app_id=app_id).order_by(
        Apk.created_at.desc()).limit(21).all()
    old_apk = None
    if len(old_apklist) > 20:
        old_apk = old_apklist[-1]
    if old_apk:
        apklist = Apk.query.filter(
            Apk.app_id == app_id, Apk.created_at < old_apk.created_at).all()
        for apk in apklist:
            apk.remove_apk()
            db.session.delete(apk)
        db.session.commit()
