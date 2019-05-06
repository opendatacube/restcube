from flask_restful import reqparse, abort, Resource, request

from datacube import Datacube
from restcube.datacube.api import get_datasets, add_datasets, get_dataset_locations
from datacube.index.hl import Doc2Dataset
from yaml import safe_load

from webargs import fields, validate
from webargs.flaskparser import parser


datasets_args = {
    "product": fields.Str(required=False),
    "url": fields.Str(required=False),
    "time": fields.DelimitedList(fields.Str(), required=False),
    "x": fields.DelimitedList(fields.Float(), required=False),
    "y": fields.DelimitedList(fields.Float(), required=False),
    "crs": fields.Str(required=False)
}

postargparser = reqparse.RequestParser()
postargparser.add_argument('product', type=str, required=False, help="Name of the Datacube product")
postargparser.add_argument('dataset_definition_urls', action="append", help="List of urls containing dataset definitions")

class Dataset(Resource):

    def get(self, ds_id):
        """Returns a dataset metadata documents (if found, otherwise, None) for the dataset with the specified dataset ID"""
        ret = dict()
        try:
            ds = list(get_datasets(id=ds_id))
            d = ds[0]
            ret = {
                "metadata": d.metadata_doc,
                "locations": get_dataset_locations(ds_id)
            }
        except ValueError:
            d = None

        return ret, 200


class Datasets(Resource):

    def get(self):
        """Uses the args to construct a Datacube query to search for datasets.
           Returns an array of dataset ids.
        """
        args = parser.parse(datasets_args, request)

        ds = get_datasets(**args)
        datasets = [ str(d.id) for d in ds ]
        print (datasets)
        return datasets, 200

    def post(self):
        """Attempts to add datasets to the datacube based on a product and dataset metadata urls
        """
        args = postargparser.parse_args()
        product = args['product']
        urls = args['dataset_definition_urls']
        print(f"product: {product} urls: {urls}")

        statuses = list(add_datasets(urls, product))

        return statuses, 200


class Locations(Resource):

    def get(self, ds_id):
        locations = get_dataset_locations(ds_id)

        return locations, 200