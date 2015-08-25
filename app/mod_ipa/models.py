#!/usr/bin/env python
# coding: utf-8

import os, sys, shutil
import zipfile
import biplist
import urlparse

from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from app import app, db

class Base(db.Model):
    __abstract__  = True

    id         = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.localtimestamp())
    updated_at = db.Column(db.DateTime, default=db.func.localtimestamp())

class Ipa(Base):

    __tablename__ = 'ipa'

    ipa_name      = db.Column(db.String(128))
    ipa_uri       = db.Column(db.String(512))
    bundle_id     = db.Column(db.String(128))
    app_version   = db.Column(db.String(64))
    build_version = db.Column(db.String(64))
    app_name      = db.Column(db.String(128))
    plist_uri     = db.Column(db.String(512))

    app_id        = db.Column(db.Integer, db.ForeignKey('app.id'), nullable = False)

    def __init__(self, app_id, ipa_name, ipa_uri, url_root):
        working_dir = os.path.dirname(ipa_uri)
        bundle_id, display_name, build_version, app_version, error_list = self.ipa_attribute(ipa_uri, working_dir)
        plist_path = self.install_plist(ipa_uri, url_root, bundle_id, app_version, display_name)

        self.app_id = app_id
        self.ipa_name = ipa_name
        self.ipa_uri = ipa_uri
        self.bundle_id = bundle_id
        self.app_version = app_version
        self.build_version = build_version
        self.app_name = display_name
        self.plist_uri = plist_path
        self.plist_uri = self.download_url(url_root)
    
    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.id, self.ipa_name)

    def remove_ipa(self):
        try:
            os.remove(self.ipa_uri)
            shutil.rmtree(os.path.dirname(self.ipa_uri))
        except OSError, e:
            app.logger.error(e)
            pass

    def download_url(self, url_root):
        plist_path = '/'.join(self.plist_uri.split('/')[1:])
        plist_path = app.config['URL_PREFIX'] + '/' + plist_path
        url_root = url_root.replace('http://', 'https://')
        plist_url = urlparse.urljoin(url_root, plist_path)
        print plist_url
        url = 'itms-services://?action=download-manifest&url={0}'.format(plist_url)
        return url

    def find(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

    def plist(self, filepath, key):
        try:
            print filepath
            plist = biplist.readPlist(os.path.expanduser(filepath))
        except IOError, e:
            app.logger.error(e)
            pass
        value = None
        if key in plist:
            value = plist[key]
        return value

    def ipa_attribute(self, ipa_path, working_dir):
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
            path = self.find('Info.plist', os.path.join(working_dir, unarchive_name))
            if not path is None:
                bundle_id = self.plist(path, 'CFBundleIdentifier')
                display_name = self.plist(path, 'CFBundleDisplayName')
                build_version = self.plist(path, 'CFBundleVersion')
                app_version = self.plist(path, 'CFBundleShortVersionString')
            else:
                error_list.append('Not found Info.plist')
            try:
                shutil.rmtree(os.path.join(working_dir, unarchive_name))
            except IOError, e:
                app.logger.error(e)
                pass
        return (bundle_id, display_name, build_version, app_version, error_list)

    def install_plist(self, ipa_file, hostname, bundle_id, app_version, display_name):
        '''
        Generate plist to install using itms-service
        '''
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
