from flask import Flask, request, abort
from flask_restful import Api
from windsweeper.resources.products import Product, Products
from windsweeper.resources.datasets import Dataset, Datasets
from windsweeper.resources.datacube import Datacube
import os

app = Flask(__name__)
api = Api(app)

api.add_resource(Product, "/products/<string:name>")
api.add_resource(Products, "/products", "/products/")
api.add_resource(Dataset, "/datasets/<string:ds_id>")
api.add_resource(Datasets, "/datasets", "/datasets/")
api.add_resource(Datacube, "/datacube")

key = os.getenv("API_KEY", None)

@app.before_request
def before_request():
    print(request.values)
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