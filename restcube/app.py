from flask import Flask
from flask_restful import Api
from restcube.resources.products import Product, Products
from restcube.resources.datasets import Dataset, Datasets
from restcube.resources.datacube import Datacube

app = Flask(__name__)
api = Api(app)

api.add_resource(Product, "/products/<string:name>")
api.add_resource(Products, "/products")
api.add_resource(Dataset, "/datasets/<string:ds_id>")
api.add_resource(Datasets, "/datasets", "/datasets/")
api.add_resource(Datacube, "/datacube")

@app.after_request
def after_request(response):
    header = response.headers
    header["Access-Control-Allow-Origin"] = "*"
    return response