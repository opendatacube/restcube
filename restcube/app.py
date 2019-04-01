from flask import Flask
from flask_restful import Api
from restcube.resources.products import Product, Products
from restcube.resources.datasets import Dataset, Datasets

app = Flask(__name__)
api = Api(app)

api.add_resource(Product, "/products/<string:name>")
api.add_resource(Products, "/products")
api.add_resource(Dataset, "/datasets/<string:ds_id>")
api.add_resource(Datasets, "/datasets", "/datasets/")
