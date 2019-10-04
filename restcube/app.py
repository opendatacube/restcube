# -*- coding: utf-8 -*-
import os

from flask import request
from flask_restful import Api

from restcube.resources.products import Product, Products
from restcube.resources.datasets import Dataset, Datasets, Locations
from restcube.resources.datacube import Datacube
from restcube.resources.tasks import Task, Tasks
from restcube.resources.index import Index
from restcube.resources.data import Data
from restcube.resources.database import Database

from restcube.factory import create_app

app = create_app()
api = Api(app)

api.add_resource(Product, "/products/<string:name>")
api.add_resource(Products, "/products", "/products/")
api.add_resource(Dataset, "/datasets/<string:ds_id>")
api.add_resource(Datasets, "/datasets", "/datasets/")
api.add_resource(Datacube, "/datacube", "/datacube/")
api.add_resource(Database, "/database", "/database/")
api.add_resource(Index, "/index", "/index/")
api.add_resource(Task, "/tasks/<string:task_id>")
api.add_resource(Tasks, "/tasks", "/tasks/")
api.add_resource(Data, "/data", "/data/")
api.add_resource(Locations, "/datasets/<string:ds_id>/locations")

allowed_origins = os.getenv("ALLOWED_ORIGINS", None)

# For authenticated requests check the request origin against a list of allowed
# origins provided by environment variables
@app.after_request
def after_request(response):
    origin = request.headers.get("Origin", None)

    if allowed_origins is not None and origin is not None and origin in str(allowed_origins).split(","):
        header = response.headers
        header["Access-Control-Allow-Origin"] = origin
        header["Access-Control-Allow-Credentials"] = True
    return response
