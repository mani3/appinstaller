#!/usr/bin/env python
# coding: utf-8

import os, sys, shutil
import zipfile
import urlparse

from datetime import datetime
from app import app, db

class Base(db.Model):
    __abstract__  = True

    id         = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

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

    def __init__(self, app_id, ipa_name, ipa_uri, bundle_id = '', app_version = '', build_version = '', app_name = '', plist = ''):
        self.app_id = app_id
        self.ipa_name = ipa_name
        self.ipa_uri = ipa_uri
        self.bundle_id = bundle_id
        self.app_version = app_version
        self.build_version = build_version
        self.app_name = app_name
        self.plist_uri = plist
    
    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.id, self.ipa_name)

    def remove_ipa(self):
        try:
            os.remove(self.ipa_uri)
            os.remove(self.plist_uri)
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