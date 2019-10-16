# -*- coding: utf-8 -*-

from flask_restful import Resource
import datacube
import re

class Health(Resource):
    """no cognito requirement for loadbalancer health check"""
    def get(self):
        return {"health": 'healthy'}, 200
