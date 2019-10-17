# -*- coding: utf-8 -*-

from flask_restful import reqparse, abort, Resource
from yaml import safe_load_all
from flask import jsonify, request
import json
from datacube import Datacube
from restcube.datacube.api import get_products, add_products
from flask_cognito import cognito_auth_required

#postargparser = reqparse.RequestParser()
#postargparser.add_argument('product_definition_url', type=str, required=True, help="URL of product defintion YAML file")

#putargparser = postargparser.copy()
#putargparser.add_argument('allow_unsafe', type=bool, default=False, help="If true, will allow unsafe product changes to be made")

class Product(Resource):

    @cognito_auth_required
    def get(self):
        """Returns product metadata document based on the name of the product.
           If multiple products have the same name, will return only a single product.
        """
        json_data = request.get_json(force=True)
        ret = dict()
        products = list(get_products(**{"name": json_data["name"]}))
        p = products[0]
        if p is not None:
            ret = {
                "name": p.name,
                "metadata": p.to_dict(),
                "measurements": p.measurements,
                "dimensions": p.dimensions
            }

        return ret, 200

    @cognito_auth_required
    def put(self):
        """Attempts to update the product specified by name.
           Uses a provided product metadata definition file specified by a URL
           Will only perform unsafe modifications if allow_unsafe is true
        """
        import urllib.request
        # args = putargparser.parse_args()
        json_data = request.get_json(force=True)
        name = json_data["name"]
        with Datacube() as dc:
            doc_request = urllib.request.urlopen(json_data['product_definition_url'])
            docs = safe_load_all(doc_request.read())

            for doc in docs:
                product = dc.index.products.from_doc(doc)
                if product.name == name:
                    try:
                        product = dc.index.products.update(
                                    product, allow_unsafe_updates=json_data['allow_unsafe'])
                    except ValueError:
                        abort(400, message="Cannot update {} without allowing unsafe modifications".format(name))

        return jsonify({"message": "{} successfully updated in datacube".format(name)})


class Products(Resource):

    @cognito_auth_required
    def get(self):
        """Returns a list of product metadata documents for all products in the datacube"""
        products = []
        for product in get_products():
            products.append(product.to_dict())
        return jsonify({"count": len(products), "products": products})


    @cognito_auth_required
    def post(self):
        """Adds a product to the database based on a product metadata definition file specified by a URL"""
        # args = postargparser.parse_args()
        json_data = request.get_json(force=True)

        ret = list()
        for product in add_products(json_data['product_definition_url']):
            ret.append({"metadata": product.to_dict()})
        return json.dump(ret)

