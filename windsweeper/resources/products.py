from flask_restful import reqparse, abort, Resource
from yaml import safe_load_all
import requests

from datacube import Datacube
from windsweeper.datacube.api import get_products, add_products


postargparser = reqparse.RequestParser()
postargparser.add_argument('product_definition_url', type=str, required=True, help="URL of product defintion YAML file")

putargparser = postargparser.copy()
putargparser.add_argument('allow_unsafe', type=bool, default=False, help="If true, will allow unsafe product changes to be made")

class Product(Resource):

    def get(self, name):
        ret = dict()
        products = list(get_products(**{"name": name}))
        p = products[0]
        if p is not None:
            ret = { "metadata": p.to_dict() }

        return ret, 200

    def put(self, name):
        import urllib.request
        args = putargparser.parse_args()

        with Datacube() as dc:
            doc_request = urllib.request.urlopen(args['product_definition_url'])
            docs = safe_load_all(doc_request.read())

            for doc in docs:
                product = dc.index.products.from_doc(doc)
                if product['name'] == name:
                    try:
                        product = dc.index.products.update(
                                    product, allow_unsafe_updates=args['allow_unsafe'])
                    except ValueError:
                        abort(400, message="Cannot update {} without allowing unsafe modifications".format(name))

        return {"message": "{} successfully updated in datacube".format(name)}, 200


class Products(Resource):
    def get(self):
        products = []
        for product in get_products():
            products.append(product.to_dict())
        return {"count": len(products), "products": products}, 200

    def post(self):
        args = postargparser.parse_args()
        ret = list()
        for product in add_products(args['product_definition_url']):
            ret.append({"metadata": product.to_dict()})

        return ret, 200

