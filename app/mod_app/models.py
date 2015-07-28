#!/usr/bin/env python
# coding: utf-8

import os
from datetime import datetime
from app import db

class App(db.Model):
    __tablename__ = 'app'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    platform = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, name = '', platform = ''):
        self.name = name
        self.platform = platform

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.id, self.name)
