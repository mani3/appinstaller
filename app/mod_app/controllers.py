#!/usr/bin/env python
# coding: utf-8

import os, sys

from flask import Blueprint, Flask, url_for, render_template, \
                  request, redirect

from app import app, db
from app.mod_app.models import App

mod_app = Blueprint('app', __name__, url_prefix='/app')

@mod_app.route('/', methods=['GET'])
def index():
    error = request.args.get('error', default=None)
    return render_template('app/index.html', error=error)

@mod_app.route('/', methods=['POST'])
def create():
    error = None
    
    return redirect(url_for('index', error=error))

@mod_app.route('/<int:id>', methods=['DELETE'])
def delete(id):
    error = None

    return redirect(url_for('index', error=error))
