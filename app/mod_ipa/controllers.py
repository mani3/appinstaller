#!/usr/bin/env python
# coding: utf-8

import os, sys

from flask import Blueprint, Flask, url_for, request, render_template, \
                  redirect, escape, Markup, make_response, send_file, Response, flash, g, \
                  jsonify

from app import db
from app.mod_ipa.models import Ipa

mod_ipa = Blueprint('ipa', __name__, url_prefix='/ipa')

@mod_ipa.route('/index/', methods=['GET'])
def index():
    return render_template('ipa/index.html')

@mod_ipa.route('/create/', methods=['POST'])
def create():
    response = { "status": 0 }
    return jsonify(ResultSet=response)

