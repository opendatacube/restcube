from flask_restful import reqparse, abort, Resource

from datacube import Datacube
from windsweeper.datacube.api import get_datasets, add_datasets
from datacube.index.hl import Doc2Dataset
from yaml import safe_load


getargparser = reqparse.RequestParser()
getargparser.add_argument('product', type=str, required=False, help="Name of the Datacube product")
getargparser.add_argument('url', type=str, required=False, help="URL of dataset definition")

postargparser = getargparser.copy()
postargparser.add_argument('dataset_definition_urls', action="append", help="List of urls containing dataset definitions")
postargparser.remove_argument('url')

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
        query = dict()
        for k, v in args.items():
            if v is not None:
                query[k] = v

        ds = get_datasets(**query)
        datasets = [ d.metadata_doc for d in ds ]
        print (datasets)
        return datasets, 200

    def post(self):
        args = postargparser.parse_args()
        product = args['product']
        urls = args['dataset_definition_urls']
        print(f"product: {product} urls: {urls}")

        statuses = list(add_datasets(urls, product))

        return statuses, 200