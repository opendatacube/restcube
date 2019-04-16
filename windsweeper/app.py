from flask import request, abort
from flask_restful import Api
from windsweeper.resources.products import Product, Products
from windsweeper.resources.datasets import Dataset, Datasets
from windsweeper.resources.datacube import Datacube
from windsweeper.resources.tasks import Tasks
from windsweeper.resources.index import Index
import os
from windsweeper.factory import create_app

app = create_app()
api = Api(app)

api.add_resource(Product, "/products/<string:name>")
api.add_resource(Products, "/products", "/products/")
api.add_resource(Dataset, "/datasets/<string:ds_id>")
api.add_resource(Datasets, "/datasets", "/datasets/")
api.add_resource(Datacube, "/datacube")
api.add_resource(Index, "/index/")
api.add_resource(Tasks, "/tasks/<string:task_id>")

key = os.getenv("API_KEY", None)

@app.before_request
def before_request():
    api_key = request.headers.get('x-api-key', None)
    if api_key is None:
        abort(401)

    if api_key != key:
        abort(401)


@app.after_request
def after_request(response):
    header = response.headers
    header["Access-Control-Allow-Origin"] = "*"
    return response
