# -*- coding: utf-8 -*-

import os
import random
import string

from flask_restful import reqparse, abort, Resource
from yaml import safe_load_all

from datacube import Datacube
from restcube.datacube.api import create_database

postargparser = reqparse.RequestParser()
postargparser.add_argument('new_db_name', type=str, required=True, help="the database to be created")
postargparser.add_argument('new_db_user', type=str, required=True, help="new user for the new database")

class Database(Resource):

    def get(self):
        pass

    def post(self):
        """ Create a new database"""
        args = postargparser.parse_args()
        ret = list()
        db_name = args['new_db_name']
        db_user = args["new_db_user"]
        db_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

        db_host = os.getenv("DB_HOSTNAME")
        db_port = os.getenv("DB_PORT")

        return create_database(db_name, db_user, db_password, db_host, db_port)

