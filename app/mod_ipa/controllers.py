#!/usr/bin/env python
# coding: utf-8

import os, sys, shutil
import zipfile
import biplist
import pytz
import urlparse

from flask import Blueprint, Flask, url_for, request, render_template, \
                  redirect, escape, Markup, make_response, send_file, \
                  Response, flash, g, jsonify
from werkzeug import secure_filename
from datetime import datetime, date, timedelta
from jinja2 import Environment, FileSystemLoader

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
            bundle_id, display_name, build_version, app_version, error_list = ipa_attribute(filepath, path)
            plist_path = install_plist(filepath, request.url_root, bundle_id, app_version, display_name)

            print request.url_root

            ipa = Ipa(app_id, filename, filepath, bundle_id, app_version, build_version, display_name, plist_path)
            ipa.plist_uri = ipa.download_url(request.url_root)
            db.session.add(ipa)
            db.session.commit()

            '''
            old_ipalist = Ipa.query.filter_by(app_id=app_id).order_by(Ipa.created_at.desc()).limit(21).all()
            old_ipa = None
            if len(old_ipalist) > 20:
                old_ipa = old_ipalist[-1]
            print old_ipa
            if old_ipa:
                ipalist = Ipa.query.filter(Ipa.app_id == app_id, Ipa.created_at < old_ipa.created_at).all()
                print ipalist
                for ipa in ipalist:
                    ipa.remove_ipa()
                    db.session.delete(ipa)
                db.session.commit()
            '''
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
        try:
            shutil.rmtree(os.path.join(working_dir, unarchive_name))
        except IOError, e:
            pass
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

def install_plist(ipa_file, hostname, bundle_id, app_version, display_name):
    filename = os.path.basename(ipa_file)
    ipa_dir = os.path.dirname(ipa_file)
    templates_path = os.path.join(app.config['BASE_DIR'], "app/templates/")
    env = Environment(loader=FileSystemLoader(templates_path, encoding='utf-8'))
    template = env.get_template('install.plist')

    upload_dir = os.path.join(app.config['URL_PREFIX'], '/'.join(ipa_dir.split('/')[1:]))
    download_path = os.path.join(upload_dir, filename)
    download_url = urlparse.urljoin(hostname, download_path)

    if display_name is None:
        display_name = filename

    renderer = {
        'download_url': download_url,
        'bundle_id': bundle_id,
        'app_version': app_version,
        'display_name': display_name
        }
    plist = template.render(renderer)
    plist_path = os.path.join(ipa_dir, 'install.plist')
    f = open(plist_path, 'w')
    f.write(plist)
    f.close
    return plist_path

