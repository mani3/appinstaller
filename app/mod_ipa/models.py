#!/usr/bin/env python
# coding: utf-8

import os, sys, shutil
import zipfile
from app import db

class Base(db.Model):
    __abstract__  = True

    id         = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.currnet_timestamp(), onupdate=db.func.current_timestamp())

class Ipa(Base):

    __tablename__ = 'ipa'

    ipa_name    = db.Column(db.String(128))
    ipa_uri     = db.Column(db.String(512))
    bundle_id   = db.Column(db.String(128))
    app_version = db.Column(db.String(64))
    app_name    = db.Column(db.String(128))

    app_id      = db.Column(db.Integer, db.ForeignKey('app.id'), nullable = False)

    def __init__(self, app_id, ipa_name, ipa_uri, bundle_id = '', app_version = '', app_name = ''):
        self.app_id = app_id
        self.ipa_name = ipa_name
        self.ipa_uri = ipa_uri
        self.bundle_id = bundle_id
    
    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.id, self.ipa_name)

    def remove_ipa(self):
        try:
            os.remove(self.ipa_uri)
        except OSError, e:
            app.logger.error(e)
            pass

