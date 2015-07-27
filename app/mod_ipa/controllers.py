#!/usr/bin/env python
# coding: utf-8

import os, sys
import zipfile
import biplist
import pytz

from flask import Blueprint, Flask, url_for, request, render_template, \
                  redirect, escape, Markup, make_response, send_file, \
                  Response, flash, g, jsonify
from werkzeug import secure_filename
from datetime import datetime, date, timedelta

from app import app, db
from app.mod_ipa.models import Ipa

mod_ipa = Blueprint('ipa', __name__, url_prefix='/ipa')

@mod_ipa.route('/index/', methods=['GET'])
def index():
    return render_template('ipa/index.html')

@mod_ipa.route('/create/', methods=['POST'])
def create():
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

            ipa_attribute(filepath, path)
   
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

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def ipa_attribute(ipa_path, working_dir):
    error_list = []
    unarchive_name = None
    bundle_id = None
    display_name = None
    build_version = None
    app_version = None
    try:
        with zipfile.ZipFile(ipa_path, 'r') as z:
            for member in z.namelist():
                if member.startswith('__MACOSX'):
                    continue
                z.extract(member, working_dir)
            unarchive_name = z.namelist()[0]
    except IOError, e:
        if os.path.exists(working_dir):
            shutil.rmtree(working_dir)
        error_list.append('Can not unarchive %s.' % filename)
        pass

    if not unarchive_name is None:
        print unarchive_name
        path = find('Info.plist', os.path.join(working_dir, unarchive_name))
        if not path is None:
            bundle_id = plist(path, 'CFBundleIdentifier')
            display_name = plist(path, 'CFBundleDisplayName')
            build_version = plist(path, 'CFBundleVersion')
            app_version = plist(path, 'CFBundleShortVersionString')
        else:
            error_list.append('Not found Info.plist')
    return (bundle_id, display_name, build_version, app_version, error_list)

def plist(filepath, key):
    try:
        print filepath
        plist = biplist.readPlist(os.path.expanduser(filepath))
    except IOError, e:
        # TODO: log
        print e
        pass
    value = None
    if key in plist:
        value = plist[key]
    return value


