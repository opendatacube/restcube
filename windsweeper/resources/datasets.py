from flask_restful import reqparse, abort, Resource

from datacube import Datacube
from windsweeper.datacube.api import get_datasets, add_datasets
from datacube.index.hl import Doc2Dataset
from yaml import safe_load


getargparser = reqparse.RequestParser()
getargparser.add_argument('product', type=str, help="Name of the Datacube product")

postargparser = getargparser.copy()
postargparser.add_argument('dataset_definition_urls', action="append", help="List of urls containing dataset definitions")

class Dataset(Resource):

    def get(self, ds_id):
        ret = dict()
        try:
            ds = list(get_datasets(id=ds_id))
            d = ds[0]
            ret = {"metadata": d.metadata_doc}
        except ValueError:
            d = None

        return ret, 200


class Datasets(Resource):

    def get(self):
        args = getargparser.parse_args()
        product = args['product']

        ds = get_datasets(**{"product": product})
        datasets = [ d.metadata.id for d in ds ]

        return {"ids": datasets}, 200

    def post(self):
        args = postargparser.parse_args()
        product = args['product']
        urls = args['dataset_definition_urls']

        statuses = list(add_datasets(urls, product))

        return statuses, 200