# -*- coding: utf-8 -*-
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database for SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

# Uploaded the ipa file directory
UPLOADED_IPA_DIR = 'app/static/uploaded_ipa'

# Path prefix
URL_PREFIX = '/appinstaller'

# Max number of saved files per an app
MAX_FILES = 20
