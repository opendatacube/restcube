from flask_restful import reqparse, abort, Resource
from yaml import safe_load_all

from datacube import Datacube


postargparser = reqparse.RequestParser()
postargparser.add_argument('product_definition_url', type=str, help="URL of product defintion YAML file")

putargparser = postargparser.copy()
putargparser.add_argument('allow_unsafe', type=bool, default=False, help="If true, will allow unsafe product changes to be made")

class Product(Resource):

    def get(self, name):
        with Datacube() as dc:
            product = dc.index.products.get_by_name(name)

            if product is None:
                abort(400, message="product {} does not exist".format(name))

            return product.to_dict(), 200

    def post(self, name):
        import urllib.request
        args = postargparser.parse_args()

        products = []
        with Datacube() as dc:
            doc_request = urllib.request.urlopen(args['product_definition_url'])
            docs = safe_load_all(doc_request.read())

            for doc in docs:
                product = dc.index.products.from_doc(doc)
                product = dc.index.products.add(product)
                products.append(product.to_dict()['name'])

        return {"message": "{} successfully added to datacube".format(" ".join(products))}, 200

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
        with Datacube() as dc:
            products = [ p.to_dict() for p in dc.index.products.get_all() ]

        return products, 200
