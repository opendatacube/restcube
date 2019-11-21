# -*- coding: utf-8 -*-

import os
import random
import string
from flask_cognito import cognito_auth_required
from flask import jsonify, request
from flask_restful import reqparse, abort, Resource
from yaml import safe_load_all

from datacube import Datacube
from restcube.datacube.api import create_database

#postargparser = reqparse.RequestParser()
#postargparser.add_argument('new_db_name', type=str, required=True, help="the database to be created")

class Database(Resource):

    @cognito_auth_required
    def get(self):
        """list all databases"""
        pass

    @cognito_auth_required
    def post(self):
        """ Create a new database"""
        #args = postargparser.parse_args()
        #ret = list()
        #db_name = args['new_db_name']
        #db_user = args['new_db_name'] + 'read'

        json_data = request.get_json(force=True)
        db_name = json_data['new_db_name']
        db_user = db_name +'read'
        db_password = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))

        db_host = os.getenv("DB_HOSTNAME")
        db_port = os.getenv("DB_PORT")

        admin_username = os.getenv("DB_USERNAME", None)
        admin_password = os.getenv("DB_PASSWORD", None)

        return jsonify(secret_name=create_database(db_name, db_user, db_password, db_host, db_port, admin_username, admin_password))

