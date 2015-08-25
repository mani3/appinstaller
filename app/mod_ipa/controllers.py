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
from app.mod_ipa.models import Ipa, Apk
from app.mod_app.models import App

mod_ipa = Blueprint('ipa', __name__, url_prefix = app.config['URL_PREFIX'] + '/ipa')

@mod_ipa.route('/', methods=['GET'])
@mod_ipa.route('/<int:app_id>', methods=['GET'])
def index(app_id=None):
    error = None
    ua = request.headers.get('User-Agent')
    applist = App.query.all()
    ipalist = []
    apklist = []
    if app_id:
        ipalist = Ipa.query.filter_by(app_id=app_id).order_by(Ipa.created_at.desc()).all()
        apklist = Apk.query.filter_by(app_id=app_id).order_by(Apk.created_at.desc()).all()

    return render_template('ipa/index.html', error=error, \
        app_list=applist, ipa_list=ipalist, apk_list=apklist, is_mobile=isMobile(ua))

@mod_ipa.route('/<int:app_id>', methods=['POST'])
def create(app_id):
    error = None
    if request.method == 'POST':
        app = App.query.filter_by(id=app_id).first()
        if not app:
            return jsonify({ 'status': 0, 'error': 'Not found application'})

        file = request.files['file']
        if app.platform == 'ios':
            if file and allowed_ipa_file(file.filename):
                filename = secure_filename(file.filename)
                path = createAppDirectory()
                filepath = os.path.join(path, filename)
                file.save(filepath)

                ipa = Ipa(app_id, filename, filepath, request.url_root)
                db.session.add(ipa)
                db.session.commit()
                removeOldIpa(app_id)
                response = { 'status': 1 }
            else:
                return jsonify({ 'status': 0, 'error': 'This file is not allowed(Not found ipa file)' })
        elif app.platform == 'android':
            if file and allowed_apk_file(file.filename):
                filename = secure_filename(file.filename)
                path = createAppDirectory()
                filepath = os.path.join(path, filename)
                file.save(filepath)

                apk = Apk(app_id, filename, filepath, request.url_root)
                db.session.add(apk)
                db.session.commit()
                removeOldApk(app_id)
                response = { 'status': 1 }
            else:
                return jsonify({ 'status': 0, 'error': 'This file is not allowed(Not found apk file)' })
        else:
            return jsonify({ 'status': 0, 'error': 'Not found application' })
    else:
        response = { 'status': 0, 'error': 'This URI is GET method only.' }
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

def isMobile(useragent):
    '''
    Check mobile device from user agent
    '''
    if 'iPhone' in useragent or 'Android' in useragent:
        return True
    return False

def createAppDirectory():
    path = app.config['UPLOADED_IPA_DIR']
    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    date = '{0}-{1:0=2d}{2:0=2d}{3:0=2d}'.format(now.date().__str__(), now.hour, now.minute, now.second)
    path = os.path.join(path, date)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def removeOldIpa(app_id):
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

def removeOldApk(app_id):
    # Remove old ipa, show latest 20
    old_apklist = Apk.query.filter_by(app_id=app_id).order_by(Apk.created_at.desc()).limit(21).all()
    old_apk = None
    if len(old_apklist) > 20:
        old_apk = old_apklist[-1]
    if old_apk:
        apklist = Apk.query.filter(Apk.app_id == app_id, Apk.created_at < old_apk.created_at).all()
        for apk in apklist:
            apk.remove_apk()
            db.session.delete(apk)
        db.session.commit()
