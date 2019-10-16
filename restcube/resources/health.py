# -*- coding: utf-8 -*-

from flask_restful import Resource
import datacube
import re

class Health(Resource):

    def get(self):
        return {"health": 'healthy'}, 200
